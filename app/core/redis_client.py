# app/core/redis_client.py
import logging
from typing import Optional
import redis.asyncio as redis

from app.core.config import settings

log = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None

def get_redis() -> redis.Redis:
    """
    Return a singleton redis.asyncio.Redis client.
    If REDIS_URL is empty or not set, returns a tiny in-memory shim that
    implements the subset of methods we need (get, set, exists, keys).
    This avoids hard crashes in dev if Redis isn't installed yet.
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    url = getattr(settings, "REDIS_URL", None)
    if url:
        log.info("Connecting to Redis at %s", url)
        _redis_client = redis.from_url(url, decode_responses=False)
        return _redis_client

    # Fallback in-memory shim (sync but compatible with await)
    log.warning("REDIS_URL not configured — using in-memory fallback (not persistent).")
    class _InMemory:
        def __init__(self):
            self._store = {}

        async def get(self, k):
            v = self._store.get(k)
            return v if v is None else (v if isinstance(v, (bytes, bytearray)) else v.encode("utf-8"))

        async def set(self, k, v):
            # accept bytes or str
            if isinstance(v, (bytes, bytearray)):
                self._store[k] = v
            else:
                self._store[k] = v if isinstance(v, str) else str(v)
            return True

        async def exists(self, k):
            return 1 if k in self._store else 0

        async def keys(self, pattern="*"):
            # simple glob support for prefix conv:
            import fnmatch
            return [k.encode("utf-8") if isinstance(k, str) else k for k in self._store.keys() if fnmatch.fnmatch(k, pattern)]

    _redis_client = _InMemory()
    return _redis_client
