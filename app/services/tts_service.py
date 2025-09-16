# app/services/tts_service.py
async def synthesize_speech_url(text: str, voice: str = "en-US") -> str | None:
    """
    Return a public URL to an audio file if using external TTS.
    For now, return None so the call flow uses <Say>.
    """
    return None
