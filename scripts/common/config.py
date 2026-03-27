from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "connecticut-scraper-challenge"
    MONGO_URL: str
    GEMINI_API_KEY: str
    GEMINI_MODEL: str

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), extra="ignore")


settings = Settings()
