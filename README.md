# Discord Bot + FastAPI Proxy for 1min.ai

A self-hosted Discord bot that gives a server access to [1min.ai](https://1min.ai) (GPT, Claude, Grok and
other models under one subscription). A small FastAPI proxy holds the API key. The bot never sees the
1min.ai key and the proxy never sees the Discord token. The two only share a secret header.

## What it uses

- **Python 3.12**
- **FastAPI** + **httpx** for the proxy that talks to 1min.ai
- **discord.py** for the bot
- **Docker Compose** to run both containers on one host

## What it does

- `/ask question:<text> web_search:<True/False>` gets an answer in the channel. `web_search` is optional
  and off by default. It lets the model use live web results.
- One cheap classifier call sorts each question by **category** and **difficulty** (easy / medium / hard),
  then routes it to the matching model. The categories are code/IT → Anthropic, factual → OpenAI and
  casual → xAI. The full routing table is in `MODELS.md`.
- The reply shows the question in bold, then the answer, then a small footer with the category, tier and
  model used.
- Replies of 1000 characters or less are posted in the channel, as a one-off answer with no memory.
  Longer replies get their own thread. Any message posted in that thread continues the same 1min.ai
  conversation.
- **Servers only.** `/ask` isn't available in DMs, so nobody can spend your credits by messaging the bot
  directly. `ALLOWED_GUILD_IDS` can also restrict which servers the bot answers in.

![Example /ask reply](docs/ask-example.png)

`documentation.html` covers the architecture, the 1min.ai API reference and a Proxmox LXC deployment guide.
`MODELS.md` lists every 1min.ai model ID.

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
| `ONE_MIN_API_KEY` | Yes | Your 1min.ai API key |
| `PROXY_SHARED_SECRET` | Yes | Any long random string. It's a shared password between the bot and the proxy and is never sent to 1min.ai |
| `DISCORD_BOT_TOKEN` | Yes | [Developer Portal](https://discord.com/developers/applications) → your app → Bot → Token |
| `MODEL_CODE_EASY`<br>`MODEL_CODE_MEDIUM`<br>`MODEL_CODE_HARD` | No | Models for programming/IT questions, one per tier (Anthropic by default) |
| `MODEL_GENERAL_EASY`<br>`MODEL_GENERAL_MEDIUM`<br>`MODEL_GENERAL_HARD` | No | Models for casual/general questions (xAI by default) |
| `MODEL_SPECIFIC_EASY`<br>`MODEL_SPECIFIC_MEDIUM`<br>`MODEL_SPECIFIC_HARD` | No | Models for factual/knowledge questions (OpenAI by default) |
| `MODEL_CLASSIFIER` | No | Cheap model that picks the category and difficulty, e.g. `gpt-4o-mini` |
| `ALLOWED_GUILD_IDS` | No | Comma-separated server IDs to restrict the bot to. Leave empty to allow any server it's invited to |
| `DEV_GUILD_ID` | No | Test server ID for instant slash-command sync. A global sync takes up to ~1 hour |
| `ONEMIN_WATCH_WEBHOOK_URL` | No | Discord webhook for the [monthly model check](#monthly-model-check). The bot itself doesn't use it |

Discord setup:
- Invite the bot with **Send Messages**, **Create Public Threads**, **Send Messages in Threads** and
  **Use Application Commands**. The thread permissions are needed for replies over 1000 characters.
- Enable the **Message Content Intent** (Developer Portal → Bot → Privileged Gateway Intents). The bot
  needs it to read follow-ups in its own answer threads, and won't log in without it. It doesn't read any
  other messages.

## Monthly model check

1min.ai renames and removes model IDs without notice. In 2026 every Claude ID moved to `us.anthropic.*`
and the `grok-4-fast-*` models were dropped, which broke every `/ask`. `scripts/check_models.py` catches
this kind of change early. It reads the model IDs each project actually uses (`.env`, then the compose
defaults, then the `config.py` defaults) and checks them against 1min.ai's public model list. That list
is at `https://api.1min.ai/models?feature=UNIFY_CHAT_WITH_AI` and needs no API key. The script then posts a
report to `ONEMIN_WATCH_WEBHOOK_URL` covering:
- missing or inactive models
- models deprecated within 90 days
- models added or removed since the last run

It uses only the standard library and runs with the host's system `python3` (3.10+). Add it to the
host's crontab with `crontab -e`. This line runs it at 09:00 on the 1st of each month:

```cron
0 9 1 * * /usr/bin/python3 /opt/discord-1min-proxy/scripts/check_models.py /opt/discord-1min-proxy /opt/read-later /opt/devops-feed-curator >> /var/log/onemin-model-check.log 2>&1
```

Pass every project dir that uses 1min.ai. Use `--dry-run` to print the report without posting it. The
exit code is 0 when everything is fine, 1 when a model is broken and 2 when the API can't be reached.
When the script reports a change, update the IDs in `config.py`, `docker-compose.yml`, `.env.example`
and the docs, plus the host's `.env` if it overrides them. Then refresh `MODELS.md`.

## Troubleshooting: "The application did not respond"

Discord expects a reply to a slash command within 3 seconds. When this error keeps happening, the cause
is almost always slow DNS inside the container. To check:

```bash
docker compose exec bot python3 -c "import socket,time; t=time.time(); socket.getaddrinfo('discord.com',443,socket.AF_INET); print(time.time()-t)"
```

The lookup should take milliseconds. The compose file already pins both services to `1.1.1.1` /
`8.8.8.8` to prevent slow lookups. If it still takes seconds, check that the `dns:` block is there and
rebuild.

## Stopping / updating

```bash
docker compose down                        # stop
git pull && docker compose up -d --build   # update
```

Two mappings live in Docker volumes, so they survive restarts and rebuilds:
- the proxy's link from each `/ask` to its 1min.ai conversation
- the bot's link from each thread to its `/ask`

## License

[MIT](LICENSE)
