# app/services/ai_service.py
import os
import httpx
from typing import Optional

# ENV vars
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # or "gemini-pro"
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_TTS_VOICE = os.getenv("DEEPGRAM_TTS_VOICE", "aura-asteria-en")  # pick any supported voice

# ---- Gemini (text) ----

def _gemini_payload(user_text: str, system_instruction: Optional[str] = None):
    """
    Build a Gemini 'generateContent' payload.
    """
    parts = []
    if system_instruction:
        parts.append({"text": f"System: {system_instruction}"})
    parts.append({"text": user_text})
    return {"contents": [{"parts": parts}]}

async def respond_to_text(user_text: str, language: str = "en") -> str:
    """
    Generate AI response to text.
    - Uses Gemini if GEMINI_API_KEY is present.
    - Falls back to a stub reply otherwise.
    """
    if not GEMINI_API_KEY:
        return f"[stub-reply:{language}] " + user_text

    # Endpoint with model in path; API key via query param
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    params = {"key": GEMINI_API_KEY}  # <-- correct auth
    headers = {"Content-Type": "application/json"}

    # Keep replies concise and helpful
    system_instruction = (
        "You are a helpful real-estate assistant for India. "
        "Be concise, friendly, and actionable. "
        "Default to English unless the user uses another language."
    )
    payload = _gemini_payload(user_text, system_instruction=system_instruction)

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, params=params, headers=headers, json=payload)
            if r.status_code != 200:
                # Attempt to provide a readable fallback message
                return f"[gemini-error:{r.status_code}] {r.text[:300]}"

            data = r.json()
            # Defensive parsing
            candidates = data.get("candidates") or []
            if not candidates:
                return "[gemini-empty] I didn't get a response. Could you rephrase?"

            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
            )
            if not parts or "text" not in parts[0]:
                return "[gemini-unexpected] Response format lacked 'text'."

            return parts[0]["text"]

    except httpx.ReadTimeout:
        return "[gemini-timeout] Network timeout while generating a reply."
    except Exception as e:
        return f"[gemini-exception] {type(e).__name__}: {str(e)[:200]}"


# ---- Deepgram (TTS) ----
async def text_to_speech(text: str, voice: Optional[str] = None) -> bytes:
    """
    Convert text to speech with Deepgram.
    Returns raw audio bytes. We keep it optional: if no key, return stub bytes.
    """
    if not DEEPGRAM_API_KEY:
        return b"[stub-audio]"

    voice = voice or DEEPGRAM_TTS_VOICE
    # Newer Deepgram TTS often uses a model param; keep both styles tolerant
    # Option A (speak endpoint with model query):
    url = f"https://api.deepgram.com/v1/speak?model={voice}"

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                return r.content
            return f"[deepgram-error:{r.status_code}] {r.text}".encode("utf-8")
    except httpx.ReadTimeout:
        return b"[deepgram-timeout]"
    except Exception as e:
        return f"[deepgram-exception] {type(e).__name__}: {str(e)[:200]}".encode("utf-8")
