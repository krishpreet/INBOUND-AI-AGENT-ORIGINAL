# app/services/stt_service.py
DTMF_MAP = {
    "1": "I want to talk to sales",
    "2": "I want to talk to support",
}

def extract_user_text(event: dict) -> str | None:
    """
    Pull a normalized 'user_text' from the webhook event:
    - Prefer speech if available (Twilio passes 'SpeechResult')
    - Fallback to DTMF (map 1/2 to simple intents)
    """
    speech = event.get("speech")
    if speech:
        s = str(speech).strip()
        return s if s else None

    digits = event.get("digits")
    if digits:
        d = str(digits).strip()
        return DTMF_MAP.get(d, f"Pressed {d}")

    return None
