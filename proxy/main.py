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
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str


@app.post("/v1/chat", response_model=ChatResponse, dependencies=[Depends(require_proxy_key)])
async def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = await conversations.get_conversation_id(request.thread_id)
    if conversation_id is None:
        conversation_id = await onemin_client.create_conversation(title=request.thread_id)
        await conversations.set_conversation_id(request.thread_id, conversation_id)

    reply = await onemin_client.chat(
        conversation_id=conversation_id,
        prompt=request.message,
        model=request.model or settings.default_model,
    )
    return ChatResponse(reply=reply)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
