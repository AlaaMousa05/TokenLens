"""Application configuration loaded from environment variables only.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str
    redis_url: str

    groq_api_key: str | None = None
    nvidia_api_key: str | None = None
    google_api_key: str | None = None


settings = Settings()
