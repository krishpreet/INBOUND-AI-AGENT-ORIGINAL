# app/routes/conversation.py
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.conversation_service import ConversationService
from app.models.conversation_models import ConversationRequest, ConversationResponse
from app.storage.conversation_store import ConversationStore

router = APIRouter()

class ProcessRequest(BaseModel):
    session_id: str
    text: str
    language: str | None = "en"

@router.post("/process", response_model=ConversationResponse)
async def process_turn(req: ProcessRequest):
    request = ConversationRequest(session_id=req.session_id, text=req.text, language=req.language)
    result = await ConversationService.handle_turn(request)
    return result

@router.post("/reset")
async def reset_session(session_id: str = Query(..., description="session_id to reset")):
    """
    Reset conversation session.
    Accepts ?session_id=... for convenience.
    """
    ctx = await ConversationStore.async_reset(session_id)
    return {"session_id": session_id, "status": "reset", "context": ctx}
