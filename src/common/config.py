from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "connecticut-scraper-challenge"

    MONGO_URI: str
    MONGO_DB_NAME: str

    GEMINI_API_KEY: str
    GEMINI_MODEL: str

    BASE_URL_CT: str
    URL_CT_TAX: str

    SNS_TOPIC_ARN: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )


def get_settings() -> Settings:
    return Settings()
