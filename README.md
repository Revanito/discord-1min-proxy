# Discord Bot + FastAPI Proxy for 1min.ai

A self-hosted Discord bot that gives a Discord server access to [1min.ai](https://1min.ai) (a multi-model AI
subscription — GPT, Claude, Gemini, etc. under one API), through a small FastAPI proxy that holds the API key
server-side and tracks conversation context per Discord thread.

The bot never sees the 1min.ai API key; the proxy never sees the Discord token. They only share a secret
header to authenticate to each other.

## What it uses

- **Python 3.12**
- **FastAPI** + **httpx** — the proxy that talks to 1min.ai
- **discord.py** — the Discord bot
- **Docker Compose** — runs both services as containers on one host

## What it does

- `@mention` the bot in a channel → it opens a thread and replies using a 1min.ai model
- Reply inside that thread (no need to mention again) → conversation context is kept, mapped to that thread
  via 1min.ai's own conversation id
- Long replies (>2000 chars) are split across multiple Discord messages
- Optional `ALLOWED_GUILD_IDS` env var restricts which Discord servers the bot responds in

See `documentation.html` for the full architecture, the 1min.ai API reference used, and a Proxmox LXC
deployment guide.

## Clone and run

```bash
git clone <this-repo-url> discord-1min-proxy
cd discord-1min-proxy
cp .env.example .env
nano .env   # fill in the values below
docker compose up -d --build
docker compose logs -f
```

## Configuring `.env`

| Variable | Required | What to put |
|---|---|---|
| `ONE_MIN_API_KEY` | Yes | Your 1min.ai API key (from your 1min.ai account/API settings) |
| `PROXY_SHARED_SECRET` | Yes | Any long random string you make up — it's just a shared password between the bot and the proxy, not sent to 1min.ai |
| `DEFAULT_MODEL` | No | A 1min.ai model identifier, e.g. `gpt-4o-mini` (default if left unset) |
| `DISCORD_BOT_TOKEN` | Yes | From the [Discord Developer Portal](https://discord.com/developers/applications) → your application → Bot → Token |
| `ALLOWED_GUILD_IDS` | No | Comma-separated Discord server IDs to restrict the bot to; leave empty to allow any server it's invited to |

Discord bot setup notes:
- Enable the **Message Content** privileged intent for the bot in the Developer Portal (Bot tab).
- Invite the bot with at least the `Send Messages`, `Create Public Threads`, and `Read Message History`
  permissions.

## Stopping / updating

```bash
docker compose down          # stop
git pull && docker compose up -d --build   # update to latest code
```

Conversation history (thread ↔ 1min.ai conversation id mapping) persists in a Docker volume, so it survives
restarts and rebuilds.
