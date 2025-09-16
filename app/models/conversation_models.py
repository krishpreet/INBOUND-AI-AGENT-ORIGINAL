from pydantic import BaseModel
from typing import Dict, Optional

class ConversationRequest(BaseModel):
    session_id: str   # unique per call/user
    text: str         # caller/lead message

class ConversationResponse(BaseModel):
    session_id: str
    user_text: str
    ai_text: str
    intent: str
    context: Optional[Dict] = {}
