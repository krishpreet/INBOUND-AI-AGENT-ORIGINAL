# app/models/knowledge.py
from pydantic import BaseModel, Field
from typing import Optional, List

class KnowledgeBase(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    documents: List[str]  # paths or raw text
