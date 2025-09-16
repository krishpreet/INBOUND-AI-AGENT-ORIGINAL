# app/telephony/twilio_provider.py
import os
import logging
from twilio.rest import Client
from fastapi.responses import Response
from app.telephony.base import TelephonyProvider

log = logging.getLogger(__name__)

# Load from env
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")  # E.164, no spaces
TWILIO_FROM_SID = os.getenv("TWILIO_FROM_SID")        # optional PN... fallback
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")

class TwilioProvider(TelephonyProvider):
    name = "TWILIO"

    def __init__(self):
        # log minimal info but not secrets
        log.debug("Initializing TwilioProvider (SID present: %s)", bool(TWILIO_ACCOUNT_SID))
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # --- Webhook I/O helpers ---
    def XMLResponse(self, xml_str: str):
        # Log a trimmed preview of the TwiML response for debugging
        preview = (xml_str[:400] + "...") if len(xml_str) > 400 else xml_str
        log.debug("Returning TwiML response preview: %s", preview)
        return Response(content=xml_str, media_type="application/xml")

    def verify_signature(self, raw: bytes, headers: dict, url: str = "", params: dict | None = None) -> bool:
        # In dev we allow all; tighten later with X-Twilio-Signature verification
        return True

    # --- TwiML builders used by CallFlowService ---
    def build_say(self, text: str, lang: str = "en") -> str:
        log.debug("build_say(lang=%s, text_len=%d)", lang, len(text or ""))
        return f"<Say language='{lang}'>{text}</Say>"

    def build_play(self, url: str) -> str:
        """Generate <Play> tag for Twilio to stream audio from URL."""
        log.info("build_play: audio url -> %s", url)
        return f"<Play>{url}</Play>"

    def build_gather(self, prompt: str, num_digits: int = 1, input_mode: str = "dtmf", lang: str = "en") -> str:
        log.debug("build_gather(input=%s,num_digits=%s,lang=%s,prompt_len=%d)",
                  input_mode, num_digits, lang, len(prompt or ""))
        return (
            f"<Gather input='{input_mode}' numDigits='{num_digits}'>"
            f"<Say language='{lang}'>{prompt}</Say>"
            f"</Gather>"
        )

    def wrap_response(self, inner: str) -> str:
        return f"<Response>{inner}</Response>"

    # --- Outbound call creation ---
    def initiate_call(self, to_number: str) -> str:
        """
        Start an outbound call via Twilio.
        Tries TWILIO_FROM_NUMBER first; falls back to TWILIO_FROM_SID if provided.
        """
        log.info("initiate_call -> to=%s, using public_base=%s", to_number, bool(PUBLIC_BASE_URL))
        if not PUBLIC_BASE_URL:
            log.warning("PUBLIC_BASE_URL not configured; returning mock sid")
            return "CA_mock_missing_public_base_url"

        from_value = TWILIO_FROM_NUMBER or TWILIO_FROM_SID
        if not from_value:
            log.error("No TWILIO_FROM_NUMBER or TWILIO_FROM_SID configured.")
            return "CA_mock_missing_from_number"

        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_value,
                url=f"{PUBLIC_BASE_URL}/voice/webhook",
            )
            log.info("Twilio create call succeeded: sid=%s", getattr(call, "sid", "UNKNOWN"))
            return call.sid
        except Exception as exc:
            # Log the full exception (traceback) for debugging
            log.exception("twilio_create_call_failed")
            # Optional: try fallback with PN SID if present and different
            try:
                if TWILIO_FROM_SID and from_value != TWILIO_FROM_SID:
                    log.info("Trying fallback from TWILIO_FROM_SID")
                    call = self.client.calls.create(
                        to=to_number,
                        from_=TWILIO_FROM_SID,
                        url=f"{PUBLIC_BASE_URL}/voice/webhook",
                    )
                    log.info("Twilio fallback create call succeeded: sid=%s", getattr(call, "sid", "UNKNOWN"))
                    return call.sid
            except Exception:
                log.exception("twilio_fallback_create_call_failed")
            return "CA_mock_TwilioRestException"
