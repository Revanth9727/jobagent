"""Config module — pydantic-settings, loads from .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ANTHROPIC_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    PROFILE_PATH: str = "data/candidate_profile.json"
    RESUME_PATH: str = "data/base_resume.json"

    @model_validator(mode="after")
    def check_required_fields(self) -> "Settings":
        missing = []
        if not self.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if not self.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
        if missing:
            keys = ", ".join(missing)
            raise ValueError(
                f"Missing required environment variable(s): {keys}. "
                f"Copy .env.example to .env and fill in the missing values."
            )
        return self


settings = Settings()
