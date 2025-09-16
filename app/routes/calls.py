# app/routes/calls.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

router = APIRouter()

# Pydantic models used by tests
class OutboundCreateRequest(BaseModel):
    caller_number: str = Field(..., example="+911112223334")
    receiver_number: str = Field(..., example="+919998887776")
    provider_call_id: Optional[str] = Field(None, example="OUT-999")

class CallRecord(BaseModel):
    caller_number: str
    receiver_number: str
    provider_call_id: str
    direction: str = "outbound"
    created_at: str
    status: str = "initiated"
    transcript: Optional[str] = None
    metadata: Dict = {}

class TranscriptUpdate(BaseModel):
    transcript: str

# Simple in-memory store for phase 1-3 tests
CALLS_DB: List[CallRecord] = []

def _find_call(provider_call_id: str) -> Optional[CallRecord]:
    for c in CALLS_DB:
        if c.provider_call_id == provider_call_id:
            return c
    return None

@router.post("/outbound", status_code=status.HTTP_201_CREATED, response_model=CallRecord)
def create_outbound_call(payload: OutboundCreateRequest):
    """
    Create an outbound call record (used by tests). The test passes provider_call_id,
    but if missing we create a mock one.
    """
    provider_id = payload.provider_call_id or f"OUT-{int(datetime.utcnow().timestamp())}"
    existing = _find_call(provider_id)
    if existing:
        raise HTTPException(status_code=409, detail="Call with provider_call_id already exists")

    rec = CallRecord(
        caller_number=payload.caller_number,
        receiver_number=payload.receiver_number,
        provider_call_id=provider_id,
        direction="outbound",
        created_at=datetime.utcnow().isoformat() + "Z",
        status="initiated",
        transcript=None,
        metadata={}
    )
    CALLS_DB.append(rec)
    return rec

@router.get("/", response_model=List[CallRecord])
def list_calls():
    """Return all recorded calls (in-memory)."""
    return CALLS_DB

@router.patch("/outbound/{provider_call_id}/transcript", response_model=CallRecord)
def update_transcript(provider_call_id: str, payload: TranscriptUpdate):
    """
    Update the transcript for a stored call. Tests may call this or you can call it from events.
    """
    rec = _find_call(provider_call_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Call not found")
    rec.transcript = payload.transcript
    # Optionally update status
    rec.status = "completed"
    return rec