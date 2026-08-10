import asyncio
import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"
_DATA_DIR.mkdir(exist_ok=True)
_PATH = _DATA_DIR / "conversations.json"
_lock = asyncio.Lock()


def _read() -> dict[str, str]:
    if not _PATH.exists():
        return {}
    return json.loads(_PATH.read_text())


async def get_conversation_id(thread_id: str) -> str | None:
    async with _lock:
        return _read().get(thread_id)


async def set_conversation_id(thread_id: str, conversation_id: str) -> None:
    async with _lock:
        data = _read()
        data[thread_id] = conversation_id
        _PATH.write_text(json.dumps(data, indent=2))
