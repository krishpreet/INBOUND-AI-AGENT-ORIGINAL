# app/services/transcript_service.py
from typing import List
from sqlalchemy import select, func
from app.core.db import async_session
from app.models.call_models import Call, TranscriptTurn

class TranscriptService:
    @staticmethod
    async def append_turn(provider_call_id: str, role: str, text: str) -> None:
        async with async_session() as session:
            res = await session.execute(select(Call).where(Call.provider_call_id == provider_call_id))
            call = res.scalar_one_or_none()
            if not call:
                call = Call(provider_call_id=provider_call_id, status="in_progress")
                session.add(call)
                await session.flush()

            res2 = await session.execute(
                select(func.coalesce(func.max(TranscriptTurn.turn_index), -1) + 1).where(TranscriptTurn.call_id == call.id)
            )
            next_idx = res2.scalar_one()
            turn = TranscriptTurn(call_id=call.id, turn_index=next_idx, role=role, text=text)
            session.add(turn)
            await session.commit()

    @staticmethod
    async def get_transcript(provider_call_id: str) -> List[TranscriptTurn]:
        async with async_session() as session:
            res = await session.execute(select(Call).where(Call.provider_call_id == provider_call_id))
            call = res.scalar_one_or_none()
            if not call:
                return []
            res2 = await session.execute(
                select(TranscriptTurn)
                .where(TranscriptTurn.call_id == call.id)
                .order_by(TranscriptTurn.turn_index.asc())
            )
            return list(res2.scalars())
