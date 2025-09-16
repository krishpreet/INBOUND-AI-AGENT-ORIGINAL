from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Event model
class CallEvent(BaseModel):
    provider_call_id: str
    event_type: str
    timestamp: str

# In-memory "DB"
events_db: List[CallEvent] = []

@router.post("/events")
async def add_event(event: CallEvent):
    events_db.append(event)
    return {"message": "Event received", "event": event}

@router.get("/events")
async def list_events():
    return events_db
