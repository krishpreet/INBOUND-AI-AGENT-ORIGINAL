from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.call_session import (
    CallSessionCreate,
    OutboundCallCreate,
    CallSessionRead,
    CallSessionList,
    StatusUpdate,
    TranscriptAppend,
)
from app.services.call_service import (
    create_call,
    create_outbound_call,
    get_call,
    list_calls,
    update_status,
    append_transcript,
)

router = APIRouter(prefix="/calls", tags=["calls"])

@router.post("/inbound", response_model=CallSessionRead, status_code=201)
async def inbound_call(payload: CallSessionCreate, db: AsyncSession = Depends(get_db)):
    created = await create_call(db, payload)
    return created

@router.post("/outbound", response_model=CallSessionRead, status_code=201)
async def outbound_call(payload: OutboundCallCreate, db: AsyncSession = Depends(get_db)):
    created = await create_outbound_call(db, payload)
    return created

@router.get("", response_model=CallSessionList)
async def list_recent_calls(limit: int = Query(default=50, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    rows = await list_calls(db, limit=limit)
    return {"items": rows}

@router.get("/{call_id}", response_model=CallSessionRead)
async def fetch_call(call_id: int, db: AsyncSession = Depends(get_db)):
    obj = await get_call(db, call_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Call not found")
    return obj

@router.patch("/{call_id}/status", response_model=CallSessionRead)
async def patch_status(call_id: int, payload: StatusUpdate, db: AsyncSession = Depends(get_db)):
    obj = await update_status(db, call_id, payload.status)
    if not obj:
        raise HTTPException(status_code=404, detail="Call not found")
    return obj

@router.post("/{call_id}/append-transcript", response_model=CallSessionRead)
async def post_append_transcript(call_id: int, payload: TranscriptAppend, db: AsyncSession = Depends(get_db)):
    obj = await append_transcript(db, call_id, payload.text)
    if not obj:
        raise HTTPException(status_code=404, detail="Call not found")
    return obj
