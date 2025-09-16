# app/telephony/webhook_parser.py
from typing import Any, Dict, Optional, Mapping

def _get(mapping: Optional[Mapping[str, Any]], key: str) -> Optional[str]:
    if not mapping:
        return None
    try:
        return mapping.get(key)
    except Exception:
        return None

def parse_incoming(
    provider_name: str,
    query,
    form,
    raw: bytes,
    headers: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    provider_name = (provider_name or "").upper()

    call_sid   = _get(form, "CallSid")      or _get(query, "CallSid")
    call_stat  = _get(form, "CallStatus")   or _get(query, "CallStatus")
    from_num   = _get(form, "From")         or _get(query, "From")
    to_num     = _get(form, "To")           or _get(query, "To")
    digits     = _get(form, "Digits")       or _get(query, "Digits")
    speech_txt = _get(form, "SpeechResult") or _get(query, "SpeechResult")

    event = {
        "provider_call_id": call_sid or "mock",
        "event": (call_stat or "answered"),
        "from": from_num,
        "to": to_num,
        "digits": digits,
        "speech": speech_txt,   # <-- NEW
        "headers": dict(headers or {}),
    }

    return event
