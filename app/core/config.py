# app/core/config.py
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Central app settings (pydantic v2 / pydantic-settings).
    Use lowercase snake_case fields internally, expose uppercase properties
    for backward compatibility (e.g. settings.PROJECT_NAME).
    """

    # --- App meta ---
    project_name: str = "Inbound AI Voice Agent"
    version: str = "0.1.0"
    database_url: str = Field(default="sqlite+aiosqlite:///./app.db", env="DATABASE_URL")

    # --- AI providers ---
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")
    deepgram_api_key: Optional[str] = Field(default=None, env="DEEPGRAM_API_KEY")
    deepgram_tts_voice: str = Field(default="aura-asteria-en", env="DEEPGRAM_TTS_VOICE")

    # --- Telephony (Twilio) ---
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_from_number: Optional[str] = Field(default=None, env="TWILIO_FROM_NUMBER")
    twilio_from_sid: Optional[str] = Field(default=None, env="TWILIO_FROM_SID")

    # Public webhook url (ngrok)
    public_base_url: Optional[str] = Field(default=None, env="PUBLIC_BASE_URL")

    # Redis
    redis_url: Optional[str] = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Debugging toggles
    telephony_debug: bool = Field(default=False, env="TELEPHONY_DEBUG")

    # pydantic-settings config for v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",       # ignore unknown env keys (handy while iterating)
        case_sensitive=False, # allow mixed-case env names
    )

    # --- Backwards-compatible uppercase properties ---
    @property
    def PROJECT_NAME(self) -> str:
        return self.project_name

    @property
    def VERSION(self) -> str:
        return self.version

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def GEMINI_API_KEY(self) -> Optional[str]:
        return self.gemini_api_key

    @property
    def GEMINI_MODEL(self) -> str:
        return self.gemini_model

    @property
    def DEEPGRAM_API_KEY(self) -> Optional[str]:
        return self.deepgram_api_key

    @property
    def DEEPGRAM_TTS_VOICE(self) -> str:
        return self.deepgram_tts_voice

    @property
    def TWILIO_ACCOUNT_SID(self) -> Optional[str]:
        return self.twilio_account_sid

    @property
    def TWILIO_AUTH_TOKEN(self) -> Optional[str]:
        return self.twilio_auth_token

    @property
    def TWILIO_FROM_NUMBER(self) -> Optional[str]:
        return self.twilio_from_number

    @property
    def TWILIO_FROM_SID(self) -> Optional[str]:
        return self.twilio_from_sid

    @property
    def PUBLIC_BASE_URL(self) -> Optional[str]:
        return self.public_base_url

    @property
    def REDIS_URL(self) -> Optional[str]:
        return self.redis_url

    @property
    def TELEPHONY_DEBUG(self) -> bool:
        return self.telephony_debug


# singleton instance used throughout the app
settings = Settings()