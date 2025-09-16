from pydantic import BaseModel, Field
from typing import Optional, List

class CallSessionCreate(BaseModel):
    provider_call_id: str = Field(..., examples=["CA12345"])
    caller_number: str = Field(..., examples=["+919900112233"])

class OutboundCallCreate(BaseModel):
    caller_number: str = Field(..., examples=["+911112223334"])
    receiver_number: str = Field(..., examples=["+919998887776"])
    provider_call_id: Optional[str] = Field(None, examples=["CA-OUT-001"])

class CallSessionRead(BaseModel):
    id: int
    provider_call_id: str
    caller_number: str
    status: str
    transcript: str

    class Config:
        from_attributes = True

class CallSessionList(BaseModel):
    items: List[CallSessionRead]

class StatusUpdate(BaseModel):
    status: str = Field(..., examples=["queued", "ringing", "in-progress", "completed", "failed"])

class TranscriptAppend(BaseModel):
    text: str = Field(..., min_length=1)
