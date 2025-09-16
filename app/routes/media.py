# app/routes/media.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from app.media.storage import resolve_audio_path
import logging

log = logging.getLogger(__name__)
router = APIRouter(prefix="/media", tags=["Media"])

@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str, request: Request):
    path = resolve_audio_path(audio_id)
    log.info("Media request for audio_id=%s from=%s", audio_id, request.client.host if request.client else "unknown")
    if not path.exists():
        log.warning("Audio not found: %s", path)
        raise HTTPException(status_code=404, detail="audio not found")
    # FileResponse will set Content-Type based on filename extension
    return FileResponse(path, filename=audio_id)
