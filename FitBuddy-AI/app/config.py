from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FitBuddy AI"
    database_url: str = "sqlite:///./fitbuddy.db"
    gemini_api_key: str = ""
    gemini_workout_model: str = "gemini-3.8-flash"
    gemini_tip_model: str = "gemini-3.8-flash"
    demo_mode: bool = True
    admin_key: str = "fitbuddy-demo-admin"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
