# app/media/storage.py
import os
import hashlib
import uuid
from pathlib import Path
from typing import Tuple

AUDIO_DIR = Path(os.getenv("AUDIO_DIR", "var/audio")).resolve()
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def make_audio_id(text: str, voice: str, ext: str = "mp3") -> str:
    # stable-ish id for caching; still allow collisions to write new uuid
    h = hashlib.sha256(f"{voice}:{text}".encode("utf-8")).hexdigest()[:16]
    return f"{h}.{ext}"

def save_audio_bytes(content: bytes, audio_id: str | None = None, ext: str = "mp3") -> Tuple[str, Path, str]:
    """
    Persist audio bytes to disk.
    Returns (audio_id, file_path, mime_type)
    """
    audio_id = audio_id or f"{uuid.uuid4().hex}.{ext}"
    file_path = AUDIO_DIR / audio_id
    file_path.write_bytes(content)
    mime = "audio/mpeg" if ext.lower() in ("mp3", "mpeg") else "audio/wav"
    return audio_id, file_path, mime

def resolve_audio_path(audio_id: str) -> Path:
    return AUDIO_DIR / audio_id
