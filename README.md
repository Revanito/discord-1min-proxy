# Discord Bot + FastAPI Proxy for 1min.ai

A self-hosted Discord bot that gives a Discord server access to [1min.ai](https://1min.ai) (a multi-model AI
subscription — GPT, Claude, Gemini, etc. under one API), through a small FastAPI proxy that holds the API key
server-side.

The bot never sees the 1min.ai API key; the proxy never sees the Discord token. They only share a secret
header to authenticate to each other.

## What it uses

- **Python 3.12**
- **FastAPI** + **httpx** — the proxy that talks to 1min.ai
- **discord.py** — the Discord bot
- **Docker Compose** — runs both services as containers on one host

## What it does

- `/ask question:<text> web_search:<True/False>` → the bot replies directly in the channel (shown as a reply
  to the `/ask` invocation) with the question and the answer; `web_search` is optional (defaults to off) and
  lets the model ground its answer with live web results
- Each `/ask` is single-shot and independent — there's no follow-up/multi-turn memory between questions
- Each question is auto-classified (via a single cheap model call) along two axes — **category**
  (code/IT → Anthropic, factual/knowledge → OpenAI, general/casual → xAI) and **difficulty**
  (easy / medium / hard) — and routed to the matching model; see `MODELS.md` for the full matrix
- The reply shows the question in bold, the answer, and a small `-#` subtext footer with the category, tier,
  and model used
- Short replies (≤1000 chars) post directly in the channel, split across multiple messages if needed; longer
  replies get their own thread instead, so the answer doesn't spam the channel
- Optional `ALLOWED_GUILD_IDS` env var restricts which Discord servers the bot responds in

![Example /ask reply](docs/ask-example.png)

See `documentation.html` for the full architecture, the 1min.ai API reference used, and a Proxmox LXC
deployment guide. See `MODELS.md` for the full list of 1min.ai model identifiers, parsed from
[1min.ai's Chat with AI API docs](https://docs.1min.ai/docs/api/chat-with-ai-api) — worth re-checking that
page occasionally, since 1min.ai adds new models regularly.

## Clone and run

```bash
git clone https://github.com/Revanito/discord-1min-proxy discord-1min-proxy
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
| `MODEL_CODE_EASY` / `MODEL_CODE_MEDIUM` / `MODEL_CODE_HARD` | No | Models used for programming/IT questions, per difficulty tier (Anthropic by default) |
| `MODEL_GENERAL_EASY` / `MODEL_GENERAL_MEDIUM` / `MODEL_GENERAL_HARD` | No | Models used for casual/general questions, per difficulty tier (xAI by default) |
| `MODEL_SPECIFIC_EASY` / `MODEL_SPECIFIC_MEDIUM` / `MODEL_SPECIFIC_HARD` | No | Models used for factual/knowledge questions, per difficulty tier (OpenAI by default) |
| `MODEL_CLASSIFIER` | No | Cheap/fast model used to classify category + difficulty before routing, e.g. `gpt-4o-mini` |
| `DISCORD_BOT_TOKEN` | Yes | From the [Discord Developer Portal](https://discord.com/developers/applications) → your application → Bot → Token |
| `ALLOWED_GUILD_IDS` | No | Comma-separated Discord server IDs to restrict the bot to; leave empty to allow any server it's invited to |
| `DEV_GUILD_ID` | No | Your test server's ID, for instant slash-command sync while developing (global sync can take ~1 hour) |

<sub>Full list of valid model identifiers in `MODELS.md`, parsed from
[docs.1min.ai/docs/api/chat-with-ai-api](https://docs.1min.ai/docs/api/chat-with-ai-api).</sub>

Discord bot setup notes:
- Invite the bot with at least the `Send Messages`, `Create Public Threads`, `Send Messages in Threads`, and
  `Use Application Commands` permissions (thread permissions are needed for replies over 1000 characters).
- No privileged intents are required (the bot doesn't read message content).

## Stopping / updating

```bash
docker compose down          # stop
git pull && docker compose up -d --build   # update to latest code
```

The proxy still creates a fresh 1min.ai conversation per `/ask` call (keyed by the Discord interaction id) and
persists that mapping in a Docker volume — this is just bookkeeping for the single-shot request, not
multi-turn memory.