# app/services/cache_redis.py
import hashlib
from typing import Optional
from app.core.redis_client import get_redis
from app.core.config import settings

# simple wrapper for TTS cache: key -> audio_id
DEFAULT_TTL = 60 * 60 * 24  # 1 day

async def tts_cache_get(key_hash: str) -> Optional[str]:
    r = get_redis()
    v = await r.get(f"tts:{key_hash}")
    if v is None:
        return None
    return v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else str(v)

async def tts_cache_set(key_hash: str, audio_id: str, ttl: int = DEFAULT_TTL):
    r = get_redis()
    await r.set(f"tts:{key_hash}", audio_id, ex=ttl)

def make_key(text: str, voice: str) -> str:
    h = hashlib.sha256(f"{voice}:{text}".encode("utf-8")).hexdigest()
    return h
