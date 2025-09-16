# app/storage/conversation_store.py
"""
Redis-backed ConversationStore with backward-compatible class API.

Provides:
 - async_get_context / async_save_turn / async_reset / async_exists / async_all_sessions
 - sync wrappers: get_context / save_turn / reset / exists / all_sessions
 - ConversationStore class exposing the same API (classmethods).

Stored under redis key: "conv:{session_id}" -> JSON object
"""

from __future__ import annotations
import json
import asyncio
from typing import Any, Dict, List, Optional

from app.core.redis_client import get_redis

_PREFIX = "conv:"

def _key(session_id: str) -> str:
    return f"{_PREFIX}{session_id}"

# -----------------------
# Async implementations
# -----------------------
async def async_get_context(session_id: str) -> Dict[str, Any]:
    r = get_redis()
    raw = await r.get(_key(session_id))
    if not raw:
        return {"history": []}
    # redis-py may return bytes or str depending on decode settings; handle both
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    try:
        return json.loads(raw)
    except Exception:
        return {"history": []}

async def async_save_turn(session_id: str, user_text: str, ai_text: str) -> None:
    r = get_redis()
    k = _key(session_id)
    raw = await r.get(k)
    if raw:
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        try:
            data = json.loads(raw)
        except Exception:
            data = {"history": []}
    else:
        data = {"history": []}
    data.setdefault("history", []).append({"user": user_text, "ai": ai_text})
    await r.set(k, json.dumps(data))

async def async_reset(session_id: str) -> Dict[str, Any]:
    r = get_redis()
    k = _key(session_id)
    initial = {"history": [], "entities": {}}
    await r.set(k, json.dumps(initial))
    return initial

async def async_exists(session_id: str) -> bool:
    r = get_redis()
    # redis-py returns int, cast to bool
    return bool(await r.exists(_key(session_id)))

async def async_all_sessions() -> List[str]:
    r = get_redis()
    keys = await r.keys(f"{_PREFIX}*")
    # redis returns list of bytes or strings
    session_ids = []
    for k in keys:
        if isinstance(k, (bytes, bytearray)):
            k = k.decode("utf-8")
        session_ids.append(k.replace(_PREFIX, ""))
    return session_ids

# -----------------------
# Sync convenience wrappers
# -----------------------
def _in_event_loop() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False

def get_context(session_id: str) -> Dict[str, Any]:
    if _in_event_loop():
        raise RuntimeError("get_context() called inside running event loop; use async_get_context() instead.")
    return asyncio.run(async_get_context(session_id))

def save_turn(session_id: str, user_text: str, ai_text: str) -> None:
    if _in_event_loop():
        raise RuntimeError("save_turn() called inside running event loop; use async_save_turn() instead.")
    return asyncio.run(async_save_turn(session_id, user_text, ai_text))

def reset(session_id: str) -> Dict[str, Any]:
    if _in_event_loop():
        raise RuntimeError("reset() called inside running event loop; use async_reset() instead.")
    return asyncio.run(async_reset(session_id))

def exists(session_id: str) -> bool:
    if _in_event_loop():
        raise RuntimeError("exists() called inside running event loop; use async_exists() instead.")
    return asyncio.run(async_exists(session_id))

def all_sessions() -> List[str]:
    if _in_event_loop():
        raise RuntimeError("all_sessions() called inside running event loop; use async_all_sessions() instead.")
    return asyncio.run(async_all_sessions())

# -----------------------
# Backwards-compatible class
# -----------------------
class ConversationStore:
    """
    Backwards-compatible interface used across the codebase.
    Use ConversationStore.async_* from async contexts if preferred.
    """

    # Async classmethods
    @classmethod
    async def async_get_context(cls, session_id: str) -> Dict[str, Any]:
        return await async_get_context(session_id)

    @classmethod
    async def async_save_turn(cls, session_id: str, user_text: str, ai_text: str) -> None:
        await async_save_turn(session_id, user_text, ai_text)

    @classmethod
    async def async_reset(cls, session_id: str) -> Dict[str, Any]:
        return await async_reset(session_id)

    @classmethod
    async def async_exists(cls, session_id: str) -> bool:
        return await async_exists(session_id)

    @classmethod
    async def async_all_sessions(cls) -> List[str]:
        return await async_all_sessions()

    # Sync classmethods (wrappers)
    @classmethod
    def get_context(cls, session_id: str) -> Dict[str, Any]:
        return get_context(session_id)

    @classmethod
    def save_turn(cls, session_id: str, user_text: str, ai_text: str) -> None:
        return save_turn(session_id, user_text, ai_text)

    @classmethod
    def reset(cls, session_id: str) -> Dict[str, Any]:
        return reset(session_id)

    @classmethod
    def exists(cls, session_id: str) -> bool:
        return exists(session_id)

    @classmethod
    def all_sessions(cls) -> List[str]:
        return all_sessions()
