import os
from app.telephony.twilio_provider import TwilioProvider
from app.telephony.exotel_provider import ExotelProvider

_provider_cache = None

def get_provider():
    global _provider_cache
    if _provider_cache:
        return _provider_cache
    name = os.getenv("VOICE_PROVIDER", "TWILIO").upper()
    if name == "EXOTEL":
        _provider_cache = ExotelProvider()
    else:
        _provider_cache = TwilioProvider()
    return _provider_cache
