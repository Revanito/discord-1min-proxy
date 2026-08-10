from fastapi import Header, HTTPException

from config import settings


async def require_proxy_key(x_proxy_key: str = Header(...)) -> None:
    if x_proxy_key != settings.proxy_shared_secret:
        raise HTTPException(401, "Invalid or missing X-Proxy-Key header")
