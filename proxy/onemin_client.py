import httpx
from fastapi import HTTPException

from config import settings

_TIMEOUT = httpx.Timeout(60.0)


def _headers() -> dict[str, str]:
    return {
        "API-KEY": settings.one_min_api_key,
        "Content-Type": "application/json",
    }


async def create_conversation(title: str) -> str:
    url = f"{settings.one_min_base_url}/api/conversations"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        try:
            resp = await client.post(url, headers=_headers(), json={"title": title})
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(502, f"1min.ai conversation creation failed: {exc}") from exc

    data = resp.json()
    conversation_id = data.get("conversation", {}).get("uuid") or data.get("uuid")
    if not conversation_id:
        raise HTTPException(502, "1min.ai response missing conversation id")
    return conversation_id


async def chat(conversation_id: str, prompt: str, model: str) -> str:
    url = f"{settings.one_min_base_url}/api/chat-with-ai"
    body = {
        "type": "UNIFY_CHAT_WITH_AI",
        "model": model,
        "promptObject": {
            "prompt": prompt,
            "conversationId": conversation_id,
        },
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        try:
            resp = await client.post(url, headers=_headers(), json=body)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(502, f"1min.ai chat request failed: {exc}") from exc

    data = resp.json()
    try:
        return data["aiRecord"]["aiRecordDetail"]["resultObject"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(502, "1min.ai response missing reply text") from exc
