from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TextRequest(BaseModel):
    text: str

@router.post("/analyze")
async def analyze_text(request: TextRequest):
    return {"intent": "inquiry", "entities": {"location": "Delhi"}}
