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
- Each question is auto-classified (via a single cheap model call) along two axes — **category**
  (code/IT → Anthropic, factual/knowledge → OpenAI, general/casual → xAI) and **difficulty**
  (easy / medium / hard) — and routed to the matching model; see `MODELS.md` for the full matrix
- The reply shows the question in bold, the answer, and a small `-#` subtext footer with the category, tier,
  and model used
- Short replies (≤1000 chars) post directly in the channel, split across multiple messages if needed, and are
  single-shot with no follow-up memory; longer replies get their own thread instead, and any message posted
  in that thread afterward continues the same 1min.ai conversation (multi-turn context, no `/ask` needed)
- Optional `ALLOWED_GUILD_IDS` env var restricts which Discord servers the bot responds in
- `/ask` in a DM to the bot is denied by default — set `ALLOWED_DM_USER_IDS` to a comma-separated list of
  Discord user IDs to let specific people (e.g. just yourself) use it in DMs; everyone else is rejected,
  so nobody can burn through your 1min.ai credits just by messaging the bot directly
- `/forget` (DM-only, same allowlist as above) deletes every message the bot has ever sent in that DM. Since
  a fresh `/ask` in a DM already starts a brand-new 1min.ai conversation every time (DMs can't have threads,
  so there's no persistent context to carry between separate `/ask` calls there in the first place), this is
  purely a visible-history cleanup — there's no separate "memory" step needed behind it

![Example /ask reply](docs/ask-example.png)

![DM rejection message for users not in ALLOWED_DM_USER_IDS](docs/dm-not-authorized.png)

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
| `MODEL_CODE_EASY`<br>`MODEL_CODE_MEDIUM`<br>`MODEL_CODE_HARD` | No | Models used for programming/IT questions, per difficulty tier (Anthropic by default) |
| `MODEL_GENERAL_EASY`<br>`MODEL_GENERAL_MEDIUM`<br>`MODEL_GENERAL_HARD` | No | Models used for casual/general questions, per difficulty tier (xAI by default) |
| `MODEL_SPECIFIC_EASY`<br>`MODEL_SPECIFIC_MEDIUM`<br>`MODEL_SPECIFIC_HARD` | No | Models used for factual/knowledge questions, per difficulty tier (OpenAI by default) |
| `MODEL_CLASSIFIER` | No | Cheap/fast model used to classify category + difficulty before routing, e.g. `gpt-4o-mini` |
| `DISCORD_BOT_TOKEN` | Yes | From the [Discord Developer Portal](https://discord.com/developers/applications) → your application → Bot → Token |
| `ALLOWED_GUILD_IDS` | No | Comma-separated Discord server IDs to restrict the bot to; leave empty to allow any server it's invited to |
| `ALLOWED_DM_USER_IDS` | No | Comma-separated Discord user IDs allowed to use `/ask` in a DM to the bot; leave empty to deny all DMs (the safe default) |
| `DEV_GUILD_ID` | No | Your test server's ID, for instant slash-command sync while developing (global sync can take ~1 hour) |
| `ONEMIN_WATCH_WEBHOOK_URL` | No | Discord webhook URL the monthly model check posts its report to (see [Monthly model check](#monthly-model-check)); not used by the bot itself |

<sub>Full list of valid model identifiers in `MODELS.md`, parsed from
[docs.1min.ai/docs/api/chat-with-ai-api](https://docs.1min.ai/docs/api/chat-with-ai-api).</sub>

Discord bot setup notes:
- Invite the bot with at least the `Send Messages`, `Create Public Threads`, `Send Messages in Threads`, and
  `Use Application Commands` permissions (thread permissions are needed for replies over 1000 characters).
- Enable the **Message Content Intent** for the bot in the
  [Discord Developer Portal](https://discord.com/developers/applications) → your application → Bot →
  Privileged Gateway Intents. This is required so the bot can read follow-up messages posted inside an
  answer thread and continue the conversation; without it the bot will fail to log in. It's the only
  privileged intent needed — the bot doesn't read message content anywhere outside of its own answer threads.
- To find your own Discord user ID for `ALLOWED_DM_USER_IDS`: enable Developer Mode (User Settings →
  Advanced), then right-click your own name anywhere and choose "Copy User ID".

## Troubleshooting: "The application did not respond" in Discord

Discord requires the bot to acknowledge a slash command within 3 seconds, or it invalidates the interaction
(the bot's reply then fails with a `404 Unknown interaction` in the logs, and Discord shows "The application
did not respond" until you retry). If this happens consistently, it's almost always slow DNS resolution
inside the container rather than an actual code/network problem — check with:

```bash
docker compose exec bot python3 -c "import socket,time; t=time.time(); socket.getaddrinfo('discord.com',443,socket.AF_INET); print(time.time()-t)"
```

If that takes multiple seconds instead of milliseconds, Docker's embedded DNS (`127.0.0.11`) is likely falling
back through a slow or unreachable upstream resolver (e.g. a local router/host resolver on an LXC/VM) before
reaching a working one. `docker-compose.yml` already pins both services to `1.1.1.1` and `8.8.8.8` via the
`dns:` key to avoid this — if you still see slow lookups after pulling the latest version, confirm that
`dns:` block is present and rebuild (`docker compose up -d --build`).

## Monthly model check

1min.ai renames and removes model IDs without notice. In 2026 every Claude ID moved to `us.anthropic.*`
and the `grok-4-fast-*` models were dropped, which broke every `/ask` until the IDs were updated.
`scripts/check_models.py` catches this early. It reads the model IDs each project actually uses
(`.env` first, then the `docker-compose.yml` defaults, then the `config.py` defaults) and checks them against
1min.ai's public model list (`https://api.1min.ai/models?feature=UNIFY_CHAT_WITH_AI`, no API key needed).
It then posts a report to a Discord webhook covering:
- models that are missing or inactive
- models due to be deprecated within 90 days
- models added to or removed from 1min.ai's list since the last run

It uses only the standard library, so it runs with the LXC's system `python3` (3.10+). There's no venv or
pip step. To set it up on the LXC:

```bash
apt install -y python3                     # usually already there on Debian 12
nano /opt/discord-1min-proxy/.env          # set ONEMIN_WATCH_WEBHOOK_URL=<your webhook URL>
python3 /opt/discord-1min-proxy/scripts/check_models.py /opt/discord-1min-proxy   # first run, posts a report
crontab -e                                 # then add the line below (09:00 on the 1st of each month)
```

```cron
0 9 1 * * /usr/bin/python3 /opt/discord-1min-proxy/scripts/check_models.py /opt/discord-1min-proxy >> /var/log/onemin-model-check.log 2>&1
```

Add more project dirs to the same command to check sibling repos that use 1min.ai, e.g.
`/opt/read-later`. A project on another LXC can't be read from here, so run the script on that LXC as
well. Use `--dry-run` to print the report without posting it or saving state. The exit code is 0 when
everything is fine, 1 when a model is broken, and 2 when the 1min.ai API can't be reached. When the
script reports a change, update the IDs in `config.py`, `docker-compose.yml`, `.env.example` and the docs,
plus the LXC's `.env` if it overrides them, then refresh `MODELS.md`.

## Stopping / updating

```bash
docker compose down          # stop
git pull && docker compose up -d --build   # update to latest code
```

The proxy creates a fresh 1min.ai conversation per `/ask` call (keyed by the Discord interaction id) and
persists that mapping in a Docker volume. For threaded answers, the bot separately persists a
Discord-thread-id → interaction-id mapping in its own volume, so it knows which 1min.ai conversation to
continue when a follow-up message arrives in that thread — both mappings survive container restarts.

## License

[MIT](LICENSE)