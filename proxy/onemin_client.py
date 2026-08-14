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
    body = {"type": "UNIFY_CHAT_WITH_AI", "title": title, "model": settings.model_general_medium}
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        try:
            resp = await client.post(url, headers=_headers(), json=body)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(502, f"1min.ai conversation creation failed: {exc}") from exc

    data = resp.json()
    conversation_id = data.get("conversation", {}).get("uuid") or data.get("uuid")
    if not conversation_id:
        raise HTTPException(502, "1min.ai response missing conversation id")
    return conversation_id


async def chat(prompt: str, model: str, conversation_id: str | None = None, web_search: bool = False) -> str:
    url = f"{settings.one_min_base_url}/api/chat-with-ai"
    prompt_object = {"prompt": prompt}
    if conversation_id is not None:
        prompt_object["conversationId"] = conversation_id
    if web_search:
        prompt_object["settings"] = {"webSearchSettings": {"webSearch": True}}

    body = {
        "type": "UNIFY_CHAT_WITH_AI",
        "model": model,
        "promptObject": prompt_object,
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


_CLASSIFY_PROMPT = (
    "Classify this question along two axes.\n"
    "Category - what kind of question it is:\n"
    "  code - programming, software, IT, sysadmin, devops questions\n"
    "  specific - factual/knowledge questions with a concrete correct answer (math, science, history, "
    "definitions, current events, research)\n"
    "  general - casual conversation, opinions, creative writing, advice, anything else\n"
    "Difficulty - how much reasoning it needs: easy, medium, or hard.\n\n"
    "Respond with exactly two words separated by a comma: category,difficulty "
    "(e.g. 'code,hard' or 'general,easy').\n\nQuestion: {question}"
)

_CATEGORIES = ("code", "specific", "general")
_DIFFICULTIES = ("easy", "medium", "hard")


async def classify(question: str) -> tuple[str, str]:
    raw = await chat(prompt=_CLASSIFY_PROMPT.format(question=question), model=settings.model_classifier)
    lowered = raw.strip().lower()
    category = next((c for c in _CATEGORIES if c in lowered), "general")
    difficulty = next((d for d in _DIFFICULTIES if d in lowered), "medium")
    return category, difficulty
