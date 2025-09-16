from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.ai_service import respond_to_text

router = APIRouter(prefix="/ai", tags=["ai"])

class AIRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = Field("en", examples=["en", "hi", "ta", "te"])
    persona: str = Field("generic", examples=["generic", "sales", "support"])

class AIResponse(BaseModel):
    reply: str

@router.post("/respond", response_model=AIResponse)
async def ai_respond(payload: AIRequest):
    reply = await respond_to_text(payload.text, language=payload.language, persona=payload.persona)
    return AIResponse(reply=reply)
