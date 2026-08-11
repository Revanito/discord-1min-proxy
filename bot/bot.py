import discord
import httpx
from discord import app_commands

from config import settings

intents = discord.Intents.default()

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


@tree.error
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    cause = error.__cause__ or error
    age = (discord.utils.utcnow() - interaction.created_at).total_seconds()
    print(
        f"[tree error] user={interaction.user} command={interaction.command.name if interaction.command else '?'} "
        f"interaction age={age:.3f}s gateway latency={client.latency:.3f}s error={cause!r}"
    )
    if not interaction.response.is_done():
        try:
            await interaction.response.send_message("Something went wrong, please try again.", ephemeral=True)
        except discord.HTTPException:
            pass


@tree.command(name="ask", description="Ask the AI a question")
@app_commands.describe(question="What do you want to ask?", web_search="Let the AI search the web for up-to-date info")
async def ask(interaction: discord.Interaction, question: str, web_search: bool = False) -> None:
    if not _guild_allowed(interaction.guild):
        await interaction.response.send_message("This bot isn't enabled in this server.", ephemeral=True)
        return

    try:
        await interaction.response.defer()
    except discord.HTTPException as exc:
        age = (discord.utils.utcnow() - interaction.created_at).total_seconds()
        print(
            f"[ask] defer() failed for {interaction.user}: {exc!r} "
            f"(interaction age {age:.3f}s, gateway latency {client.latency:.3f}s)"
        )
        raise

    try:
        result = await _ask_proxy(interaction.id, question, web_search=web_search)
    except httpx.HTTPError as exc:
        await interaction.followup.send(f"Sorry, I couldn't reach the AI proxy: {exc}")
        return

    search_note = " · web search: on" if web_search else ""
    footer = f"-# tier: {result['tier']} · model: {result['model']}{search_note}"
    full = f"**{question}**\n{result['reply']}\n{footer}"

    chunks = [full[i : i + 2000] for i in range(0, len(full), 2000)]
    await interaction.followup.send(chunks[0])
    for chunk in chunks[1:]:
        await interaction.channel.send(chunk)


def main() -> None:
    client.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
