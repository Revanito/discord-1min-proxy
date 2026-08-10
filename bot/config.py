import os


class Settings:
    discord_bot_token: str = os.environ["DISCORD_BOT_TOKEN"]
    proxy_url: str = os.environ.get("PROXY_URL", "http://proxy:8000")
    proxy_shared_secret: str = os.environ["PROXY_SHARED_SECRET"]
    allowed_guild_ids: set[int] = {
        int(g) for g in os.environ.get("ALLOWED_GUILD_IDS", "").split(",") if g.strip()
    }
    dev_guild_id: int | None = (
        int(os.environ["DEV_GUILD_ID"]) if os.environ.get("DEV_GUILD_ID") else None
    )


settings = Settings()
