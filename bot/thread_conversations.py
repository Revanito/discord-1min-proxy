import asyncio
import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"
_DATA_DIR.mkdir(exist_ok=True)
_PATH = _DATA_DIR / "thread_conversations.json"
_lock = asyncio.Lock()


def _read() -> dict[str, int]:
    if not _PATH.exists():
        return {}
    return json.loads(_PATH.read_text())


async def get_proxy_thread_id(discord_thread_id: int) -> int | None:
    async with _lock:
        return _read().get(str(discord_thread_id))


async def set_proxy_thread_id(discord_thread_id: int, proxy_thread_id: int) -> None:
    async with _lock:
        data = _read()
        data[str(discord_thread_id)] = proxy_thread_id
        _PATH.write_text(json.dumps(data, indent=2))
