from dotenv import load_dotenv
import os, pathlib
dotenv_path = pathlib.Path(".env").resolve()
print("Using .env at:", dotenv_path)
load_dotenv(dotenv_path=dotenv_path)
print("SID:", os.getenv("TWILIO_ACCOUNT_SID"))
print("TOKEN set:", bool(os.getenv("TWILIO_AUTH_TOKEN")))
print("FROM:", os.getenv("TWILIO_FROM_NUMBER"))
print("PUBLIC:", os.getenv("PUBLIC_BASE_URL"))
