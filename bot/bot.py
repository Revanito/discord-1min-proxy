import re

import discord
import httpx

from config import settings

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

MENTION_RE = re.compile(r"<@!?\d+>")


def _strip_mention(text: str) -> str:
    return MENTION_RE.sub("", text).strip()


async def _ask_proxy(thread_id: int, message: str) -> str:
    async with httpx.AsyncClient(timeout=90.0) as http:
        resp = await http.post(
            f"{settings.proxy_url}/v1/chat",
            headers={"X-Proxy-Key": settings.proxy_shared_secret},
            json={"thread_id": str(thread_id), "message": message},
        )
    resp.raise_for_status()
    return resp.json()["reply"]


async def _send_reply(channel: discord.abc.Messageable, text: str) -> None:
    for i in range(0, len(text), 2000):
        await channel.send(text[i : i + 2000])


@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    if settings.allowed_guild_ids and (
        message.guild is None or message.guild.id not in settings.allowed_guild_ids
    ):
        return

    is_mention = client.user in message.mentions
    is_continuation = (
        isinstance(message.channel, discord.Thread)
        and message.channel.owner_id == client.user.id
    )
    if not is_mention and not is_continuation:
        return

    prompt = _strip_mention(message.content) if is_mention else message.content
    if not prompt:
        return

    if is_mention and not isinstance(message.channel, discord.Thread):
        thread = await message.create_thread(name=prompt[:80] or "Chat")
    else:
        thread = message.channel

    async with thread.typing():
        try:
            reply = await _ask_proxy(thread.id, prompt)
        except httpx.HTTPError as exc:
            await thread.send(f"Sorry, I couldn't reach the AI proxy: {exc}")
            return

    await _send_reply(thread, reply)


def main() -> None:
    client.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
