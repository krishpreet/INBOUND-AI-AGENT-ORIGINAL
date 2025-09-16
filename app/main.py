# app/main.py
from dotenv import load_dotenv
load_dotenv()  # ensure .env is loaded before anything else

# configure logging early so later imports can log safely
from app.core.logger import configure_logging
configure_logging()

import logging
import os
from fastapi import FastAPI

# Import settings + DB AFTER logging is configured so logs show up with proper config
from app.core.config import settings
from app.core.db import engine, Base

# Import routers (must be after settings/db so they can rely on config if needed)
from app.routes import health, calls, events, ai, conversation, voice, knowledge
from app.routes import media as media_routes

logger = logging.getLogger(__name__)
logger.info(
    "ENV: GEMINI=%s | DEEPGRAM=%s | TWILIO_SID=%s",
    bool(os.getenv("GEMINI_API_KEY")),
    bool(os.getenv("DEEPGRAM_API_KEY")),
    bool(os.getenv("TWILIO_ACCOUNT_SID")),
)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)


@app.on_event("startup")
async def on_startup():
    """
    Create DB tables on app startup (simple dev behavior).
    In production use Alembic migrations instead of create_all.
    """
    try:
        logger.info("Running DB initialization / create_all")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("DB initialization complete.")
    except Exception as exc:
        logger.exception("DB initialization failed: %s", exc)


# Routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(calls.router, prefix="/calls", tags=["Calls"])
app.include_router(events.router, prefix="/events", tags=["Call Events"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(conversation.router, prefix="/conversation", tags=["Conversation"])
app.include_router(voice.router)              # voice endpoints (Twilio/webhooks)
app.include_router(media_routes.router)       # media serving (audio assets)
app.include_router(knowledge.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Inbound AI Voice Agent API"}