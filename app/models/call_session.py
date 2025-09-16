from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.db import Base

class CallSession(Base):
    __tablename__ = "call_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider_call_id: Mapped[str] = mapped_column(String(128), index=True)
    caller_number: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="started")
    transcript: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
