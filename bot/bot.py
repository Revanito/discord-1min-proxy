import discord
import httpx
from discord import app_commands

import thread_conversations
from config import settings

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def _ask_proxy(
    thread_id: int, message: str, channel_label: str, web_search: bool = False
) -> dict:
    async with httpx.AsyncClient(timeout=90.0) as http:
        resp = await http.post(
            f"{settings.proxy_url}/v1/chat",
            headers={"X-Proxy-Key": settings.proxy_shared_secret},
            json={
                "thread_id": str(thread_id),
                "message": message,
                "web_search": web_search,
                "channel_label": channel_label,
            },
        )
    resp.raise_for_status()
    return resp.json()


def _channel_label(channel: discord.abc.Messageable, guild: discord.Guild | None) -> str:
    if guild is None:
        return "DIRECT MESSAGE"
    if isinstance(channel, discord.Thread):
        parent = f"#{channel.parent.name} > " if channel.parent else ""
        return f"{parent}{channel.name}"
    return f"#{getattr(channel, 'name', 'unknown')}"


def _ask_allowed(interaction: discord.Interaction) -> bool:
    if interaction.guild is not None:
        return not settings.allowed_guild_ids or interaction.guild.id in settings.allowed_guild_ids
    return interaction.user.id in settings.allowed_dm_user_ids


_THREAD_CHAR_THRESHOLD = 1000


def _chunk(text: str, size: int = 2000) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


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
    if not _ask_allowed(interaction):
        message = (
            "This bot isn't enabled in this server."
            if interaction.guild is not None
            else "You're not authorized to use this bot in DMs."
        )
        await interaction.response.send_message(message, ephemeral=True)
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

    channel_label = _channel_label(interaction.channel, interaction.guild)
    try:
        result = await _ask_proxy(interaction.id, question, channel_label, web_search=web_search)
    except httpx.HTTPError as exc:
        await interaction.followup.send(f"Sorry, I couldn't reach the AI proxy: {exc}")
        return

    search_note = " · web search: on" if web_search else ""
    footer = f"-# category: {result['category']} · tier: {result['tier']} · model: {result['model']}{search_note}"
    reply = result["reply"]

    if len(reply) <= _THREAD_CHAR_THRESHOLD or interaction.guild is None:
        # DMs can't have threads, so long replies there just get chunked in-place too.
        full = f"**{question}**\n{reply}\n{footer}"
        chunks = _chunk(full)
        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)
        return

    teaser = await interaction.followup.send(
        f"**{question}**\n{footer}\n-# 🧵 answer in thread below", wait=True
    )
    thread_name = question if len(question) <= 100 else f"{question[:97]}..."
    thread = await interaction.channel.create_thread(name=thread_name, message=teaser)
    await thread_conversations.set_proxy_thread_id(thread.id, interaction.id)
    for chunk in _chunk(reply):
        await thread.send(chunk)


@tree.command(name="forget", description="Delete the bot's messages in this DM")
async def forget(interaction: discord.Interaction) -> None:
    if interaction.guild is not None:
        await interaction.response.send_message("This command only works in DMs.", ephemeral=True)
        return
    if interaction.user.id not in settings.allowed_dm_user_ids:
        await interaction.response.send_message("You're not authorized to use this bot in DMs.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    deleted = 0
    async for message in interaction.channel.history(limit=None):
        if message.author.id == client.user.id:
            try:
                await message.delete()
                deleted += 1
            except discord.HTTPException:
                pass

    await interaction.followup.send(f"Deleted {deleted} message{'s' if deleted != 1 else ''}.", ephemeral=True)


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot or not isinstance(message.channel, discord.Thread):
        return

    proxy_thread_id = await thread_conversations.get_proxy_thread_id(message.channel.id)
    if proxy_thread_id is None:
        return

    channel_label = _channel_label(message.channel, message.guild)
    async with message.channel.typing():
        try:
            result = await _ask_proxy(proxy_thread_id, message.content, channel_label)
        except httpx.HTTPError as exc:
            await message.channel.send(f"Sorry, I couldn't reach the AI proxy: {exc}")
            return

    footer = f"-# category: {result['category']} · tier: {result['tier']} · model: {result['model']}"
    full = f"{result['reply']}\n{footer}"
    for chunk in _chunk(full):
        await message.channel.send(chunk)


def main() -> None:
    client.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
