# app/jobs/tts_worker.py
"""
Background TTS worker stub.
In Phase 7 we're leaving job queue wiring minimal. For production use RQ/Celery/Temporal etc.
"""
import asyncio
from app.services.ai_service import text_to_speech
from app.media.storage import save_audio_bytes

async def generate_and_store_audio(text: str, audio_id: str, voice: str = "aura-asteria-en"):
    audio_bytes = await text_to_speech(text, voice=voice)
    if isinstance(audio_bytes, (bytes, bytearray)):
        save_audio_bytes(audio_bytes, audio_id=audio_id, ext="mp3")
        return True
    return False
