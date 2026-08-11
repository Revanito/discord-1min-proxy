import discord
import httpx
from discord import app_commands

from config import settings

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def _ask_proxy(thread_id: int, message: str, web_search: bool = False) -> dict:
    async with httpx.AsyncClient(timeout=90.0) as http:
        resp = await http.post(
            f"{settings.proxy_url}/v1/chat",
            headers={"X-Proxy-Key": settings.proxy_shared_secret},
            json={"thread_id": str(thread_id), "message": message, "web_search": web_search},
        )
    resp.raise_for_status()
    return resp.json()


async def _send_reply(channel: discord.abc.Messageable, text: str) -> None:
    for i in range(0, len(text), 2000):
        await channel.send(text[i : i + 2000])


def _guild_allowed(guild: discord.Guild | None) -> bool:
    return not settings.allowed_guild_ids or (guild is not None and guild.id in settings.allowed_guild_ids)


@client.event
async def on_ready() -> None:
    if settings.dev_guild_id:
        guild = discord.Object(id=settings.dev_guild_id)
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
    else:
        await tree.sync()
    print(f"Logged in as {client.user}")


@tree.command(name="ask", description="Ask the AI a question")
@app_commands.describe(question="What do you want to ask?", web_search="Let the AI search the web for up-to-date info")
async def ask(interaction: discord.Interaction, question: str, web_search: bool = False) -> None:
    age = discord.utils.utcnow() - interaction.created_at
    print(f"[ask] interaction age at handler entry: {age.total_seconds():.3f}s")

    if not _guild_allowed(interaction.guild):
        await interaction.response.send_message("This bot isn't enabled in this server.", ephemeral=True)
        return

    defer_start = discord.utils.utcnow()
    await interaction.response.defer()
    print(f"[ask] defer() took {(discord.utils.utcnow() - defer_start).total_seconds():.3f}s")
    starter = await interaction.followup.send(f"**{question}**", wait=True)
    thread = await interaction.channel.create_thread(
        name=question[:80] or "Question", message=starter
)

    async with thread.typing():
        try:
            result = await _ask_proxy(thread.id, question, web_search=web_search)
        except httpx.HTTPError as exc:
            await thread.send(f"Sorry, I couldn't reach the AI proxy: {exc}")
            return

    await _send_reply(thread, result["reply"])
    search_note = " · web search: on" if web_search else ""
    await thread.send(f"-# tier: {result['tier']} · model: {result['model']}{search_note}")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    if not _guild_allowed(message.guild):
        return
    if not (isinstance(message.channel, discord.Thread) and message.channel.owner_id == client.user.id):
        return

    async with message.channel.typing():
        try:
            result = await _ask_proxy(message.channel.id, message.content)
        except httpx.HTTPError as exc:
            await message.channel.send(f"Sorry, I couldn't reach the AI proxy: {exc}")
            return

    await _send_reply(message.channel, result["reply"])


def main() -> None:
    client.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
