import logging

from fastapi import Depends, FastAPI
from pydantic import BaseModel

import conversations
import onemin_client
from auth import require_proxy_key
from config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("proxy")

app = FastAPI(title="1min.ai Discord Proxy")


class ChatRequest(BaseModel):
    thread_id: str
    message: str
    web_search: bool = False
    channel_label: str = "unknown"


class ChatResponse(BaseModel):
    reply: str
    model: str
    category: str
    tier: str


_MODEL_MATRIX = {
    "code": {
        "easy": settings.model_code_easy,
        "medium": settings.model_code_medium,
        "hard": settings.model_code_hard,
    },
    "general": {
        "easy": settings.model_general_easy,
        "medium": settings.model_general_medium,
        "hard": settings.model_general_hard,
    },
    "specific": {
        "easy": settings.model_specific_easy,
        "medium": settings.model_specific_medium,
        "hard": settings.model_specific_hard,
    },
}


@app.post("/v1/chat", response_model=ChatResponse, dependencies=[Depends(require_proxy_key)])
async def chat(request: ChatRequest) -> ChatResponse:
    logger.info(f"[{request.channel_label}] request received (thread_id={request.thread_id})")

    conversation_id = await conversations.get_conversation_id(request.thread_id)
    if conversation_id is None:
        conversation_id = await onemin_client.create_conversation(title=request.thread_id)
        await conversations.set_conversation_id(request.thread_id, conversation_id)

    category, tier = await onemin_client.classify(request.message)
    model = _MODEL_MATRIX[category][tier]

    reply = await onemin_client.chat(
        conversation_id=conversation_id,
        prompt=request.message,
        model=model,
        web_search=request.web_search,
    )
    logger.info(f"[{request.channel_label}] answered - category={category} tier={tier} model={model}")
    return ChatResponse(reply=reply, model=model, category=category, tier=tier)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
