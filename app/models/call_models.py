# app/models/call_models.py
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, func, Text
from app.core.db import Base

class Call(Base):
    __tablename__ = "calls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_call_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    from_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)  # ringing, in_progress, completed, failed
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    events = relationship("CallEvent", back_populates="call", cascade="all, delete-orphan", lazy="selectin")
    transcript_turns = relationship("TranscriptTurn", back_populates="call", cascade="all, delete-orphan", lazy="selectin")

class CallEvent(Base):
    __tablename__ = "call_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)  # answered, digits, speech, completed, ai_reply, prompt
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    call = relationship("Call", back_populates="events")

class TranscriptTurn(Base):
    __tablename__ = "transcript_turns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), index=True)
    turn_index: Mapped[int] = mapped_column(Integer, index=True)
    role: Mapped[str] = mapped_column(String(16))  # "user" | "ai"
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    call = relationship("Call", back_populates="transcript_turns")
