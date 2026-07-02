from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.maple.ai_core import ask_maple_ai_stream
from app.maple.chat import build_chat_context, chat_maple


router = APIRouter(prefix="/maple/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    anime_id: int | None = None
    user_id: str = "guest"


@router.post("/")
def chat(req: ChatRequest):
    try:
        return chat_maple(req.message, req.anime_id, req.user_id)
    except Exception:
        return {
            "type": "fallback",
            "response": "Maple is temporarily unavailable. Try again soon.",
            "context_used": False,
            "memory_used": False,
        }


@router.post("/stream")
def chat_stream(req: ChatRequest):
    context = build_chat_context(req.message, req.anime_id, req.user_id)

    def generate():
        for token in ask_maple_ai_stream(req.message, context):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")
