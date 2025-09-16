# app/core/db.py
"""
Async SQLAlchemy engine and helpers.

Exports:
- engine : AsyncEngine  (usable by app.startup for metadata.create_all)
- Base   : declarative_base()
- get_engine() -> AsyncEngine
- check_db() -> bool (async)
"""

from __future__ import annotations
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.core.config import settings

log = logging.getLogger(__name__)

# Declarative base for models
Base = declarative_base()

# Internal engine holder
_engine: Optional[AsyncEngine] = None

def get_engine() -> AsyncEngine:
    """Return a singleton AsyncEngine. Creates it on first call."""
    global _engine
    if _engine is None:
        # Create the async engine from configured DATABASE_URL
        # Example default: sqlite+aiosqlite:///./var/app.db
        _engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
        log.info("Created async engine for %s", settings.DATABASE_URL)
    return _engine

# Provide module-level name 'engine' for code expecting it.
engine = get_engine()

async def check_db() -> bool:
    """
    Lightweight DB connectivity check.
    Returns True if a simple SELECT works.
    """
    try:
        eng = get_engine()
        async with eng.connect() as conn:
            # run a trivial statement
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        log.exception("DB healthcheck failed: %s", exc)
        return False
