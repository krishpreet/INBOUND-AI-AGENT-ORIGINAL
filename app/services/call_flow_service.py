# app/services/call_flow_service.py
import os
import hashlib
import logging
from typing import Optional

from app.telephony.base import TelephonyProvider
from app.services.ai_service import respond_to_text, text_to_speech
from app.models.conversation_models import ConversationRequest
from app.services.conversation_service import ConversationService
from app.services.tts_cache import TTSCache
from app.media.storage import save_audio_bytes

log = logging.getLogger(__name__)

# Default voice
DEFAULT_VOICE = os.getenv("DEEPGRAM_TTS_VOICE", "aura-asteria-en")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

WELCOME_PROMPT = "Hi! I'm your AI assistant. You can speak, or press 1 for sales, 2 for support."

class CallFlowService:
    @staticmethod
    async def handle_incoming_event(event: dict, provider: TelephonyProvider) -> str:
        """
        Phase 6.5: AI-driven multi-turn with TTS caching + audio serve.
        Returns TwiML XML string.
        """
        try:
            session_id = event.get("provider_call_id", "sess-mock")
            # extract user text either speech or DTMF mapping
            user_text = CallFlowService._extract_user_text(event)

            # First turn → prompt for speech or DTMF
            if not user_text:
                gather = provider.build_gather(
                    prompt=WELCOME_PROMPT,
                    num_digits=1,
                    input_mode="speech dtmf",
                    lang="en"
                )
                return provider.wrap_response(gather)

            # AI turn → call ConversationService (assume async)
            req = ConversationRequest(session_id=session_id, text=user_text, language="en")
            result = await ConversationService.handle_turn(req)

            reply_text = result.ai_text or "[sorry] I couldn't process that."

            # Build TTS: try cache first
            voice = DEFAULT_VOICE
            key_raw = f"{voice}:{reply_text}"
            key_hash = hashlib.sha256(key_raw.encode("utf-8")).hexdigest()

            cached = TTSCache.get(key_hash)
            audio_id = None
            if cached:
                audio_id = cached.get("audio_id")

            if not audio_id:
                # call TTS (ai_service.text_to_speech returns bytes)
                try:
                    tts_bytes = await text_to_speech(reply_text, voice=voice)
                    if isinstance(tts_bytes, (bytes, bytearray)):
                        # persist to disk
                        # use .mp3 extension (Deepgram returns mp3 by default often)
                        audio_id = f"{key_hash}.mp3"
                        save_audio_bytes(tts_bytes, audio_id=audio_id, ext="mp3")
                        # cache meta
                        TTSCache.set(key_hash, {"audio_id": audio_id, "mime": "audio/mpeg"})
                    else:
                        # text or error prefix returned — fall back to Say
                        log.warning("TTS returned non-bytes; falling back to Say: %s", repr(tts_bytes)[:200])
                        audio_id = None
                except Exception as e:
                    log.exception("tts_failure")
                    audio_id = None

            # Build response TwiML: Play + Gather, or fallback to Say + Gather
            if audio_id and PUBLIC_BASE_URL:
                play_url = f"{PUBLIC_BASE_URL}/media/audio/{audio_id}"
                play = provider.build_play(play_url)
                follow_up = provider.build_gather(
                    prompt="You can continue, or press 1 for sales, 2 for support.",
                    num_digits=1,
                    input_mode="speech dtmf",
                    lang="en"
                )
                return provider.wrap_response(play + follow_up)
            else:
                # fallback to Say
                say = provider.build_say(reply_text, lang="en")
                follow_up = provider.build_gather(
                    prompt="You can continue, or press 1 for sales, 2 for support.",
                    num_digits=1,
                    input_mode="speech dtmf",
                    lang="en"
                )
                return provider.wrap_response(say + follow_up)

        except Exception:
            log.exception("call_flow_failure")
            # safe fallback TwiML
            fallback = (
                "<Response>"
                "<Say language='en'>We hit a temporary error. Please say that again, or press 1 for sales, 2 for support.</Say>"
                "<Gather input='speech dtmf' numDigits='1' timeout='5' />"
                "</Response>"
            )
            return fallback

    @staticmethod
    def _extract_user_text(event: dict) -> Optional[str]:
        # If speech present -> use it; if digits present, map to intent text; else None
        speech = event.get("speech")
        digits = event.get("digits")
        if speech:
            return speech
        if digits:
            # map digits to canned phrases
            mapping = {"1": "I want to talk to sales", "2": "I want to talk to support"}
            return mapping.get(digits)
        return None
