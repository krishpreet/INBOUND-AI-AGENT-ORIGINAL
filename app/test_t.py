
from dotenv import load_dotenv
load_dotenv()
import os
from twilio.rest import Client
sid=os.getenv("TWILIO_ACCOUNT_SID"); tok=os.getenv("TWILIO_AUTH_TOKEN")
frm=os.getenv("TWILIO_FROM_NUMBER")
to = "+919811940229"   # your test target
print("Using:", sid, frm)
try:
    client = Client(sid, tok)
    call = client.calls.create(to=to, from_=frm, url="https://example.com/voice/webhook")
    print("Call SID:", call.sid)
except Exception as e:
    print("Twilio error:", type(e).__name__, str(e))
