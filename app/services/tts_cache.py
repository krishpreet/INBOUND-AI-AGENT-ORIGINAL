# app/services/tts_cache.py
from typing import Optional

class TTSCache:
    """
    Minimal in-memory cache: key -> {audio_id, mime, path}
    Key convention: f"{voice}:{text}" (you may hash externally).
    """
    _store: dict[str, dict] = {}

    @classmethod
    def get(cls, key: str) -> Optional[dict]:
        return cls._store.get(key)

    @classmethod
    def set(cls, key: str, value: dict) -> None:
        cls._store[key] = value

    @classmethod
    def clear(cls) -> None:
        cls._store.clear()
