from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Industrial IoT Monitor"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = ""
    REDIS_STREAM_NAME: str = "measurements"

    # Ingestion: "async" queues measurements via Redis Stream,
    # "sync" writes directly to the database.
    INGESTION_MODE: str = "async"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("DATABASE_URL", "REDIS_URL")
    @classmethod
    def must_not_be_empty(cls, v: str, info) -> str:
        if not v:
            raise ValueError(f"{info.field_name} must be set in .env file")
        return v


settings = Settings()
