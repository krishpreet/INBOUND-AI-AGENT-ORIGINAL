# app/services/call_service.py
from typing import Optional, Dict, Any, List
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from app.core.db import async_session
from app.models.call_models import Call, CallEvent

class CallService:
    @staticmethod
    async def get_or_create_call(provider_call_id: str, from_number: Optional[str] = None, to_number: Optional[str] = None) -> Call:
        async with async_session() as session:
            res = await session.execute(select(Call).where(Call.provider_call_id == provider_call_id))
            call = res.scalar_one_or_none()
            if call:
                return call
            call = Call(provider_call_id=provider_call_id, from_number=from_number, to_number=to_number, status="in_progress")
            session.add(call)
            await session.commit()
            await session.refresh(call)
            return call

    @staticmethod
    async def set_status(provider_call_id: str, status: str, ended_at: Optional[str] = None) -> None:
        async with async_session() as session:
            await session.execute(
                update(Call)
                .where(Call.provider_call_id == provider_call_id)
                .values(status=status, ended_at=ended_at)
            )
            await session.commit()

    @staticmethod
    async def log_event(provider_call_id: str, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        async with async_session() as session:
            res = await session.execute(select(Call).where(Call.provider_call_id == provider_call_id))
            call = res.scalar_one_or_none()
            if not call:
                call = Call(provider_call_id=provider_call_id, status="in_progress")
                session.add(call)
                await session.flush()
            evt = CallEvent(call_id=call.id, event_type=event_type, payload=payload or {})
            session.add(evt)
            await session.commit()

    @staticmethod
    async def get_call(provider_call_id: str) -> Optional[Call]:
        async with async_session() as session:
            res = await session.execute(
                select(Call)
                .options(joinedload(Call.events), joinedload(Call.transcript_turns))
                .where(Call.provider_call_id == provider_call_id)
            )
            return res.scalar_one_or_none()

    @staticmethod
    async def list_events(provider_call_id: str) -> List[CallEvent]:
        async with async_session() as session:
            res = await session.execute(
                select(CallEvent)
                .join(Call, CallEvent.call_id == Call.id)
                .where(Call.provider_call_id == provider_call_id)
                .order_by(CallEvent.created_at.asc())
            )
            return list(res.scalars())
