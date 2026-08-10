from fastapi import Depends, FastAPI
from pydantic import BaseModel

import conversations
import onemin_client
from auth import require_proxy_key
from config import settings

app = FastAPI(title="1min.ai Discord Proxy")


class ChatRequest(BaseModel):
    thread_id: str
    message: str
    web_search: bool = False


class ChatResponse(BaseModel):
    reply: str
    model: str
    tier: str


_TIER_MODELS = {
    "easy": settings.model_easy,
    "medium": settings.model_medium,
    "hard": settings.model_hard,
}


@app.post("/v1/chat", response_model=ChatResponse, dependencies=[Depends(require_proxy_key)])
async def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = await conversations.get_conversation_id(request.thread_id)
    if conversation_id is None:
        conversation_id = await onemin_client.create_conversation(title=request.thread_id)
        await conversations.set_conversation_id(request.thread_id, conversation_id)

    tier = await onemin_client.classify_difficulty(request.message)
    model = _TIER_MODELS[tier]

    reply = await onemin_client.chat(
        conversation_id=conversation_id,
        prompt=request.message,
        model=model,
        web_search=request.web_search,
    )
    return ChatResponse(reply=reply, model=model, tier=tier)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
