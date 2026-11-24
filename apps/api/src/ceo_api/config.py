"""Process settings loaded from the environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://ceo:ceo@localhost:5432/ceo"
    redis_url: str = "redis://localhost:6379/0"
    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key_id: str = "ceo"
    s3_secret_access_key: str = "ceo-secret"
    s3_bucket: str = "ceo-artifacts"
    s3_region: str = "us-east-1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000


def get_settings() -> Settings:
    return Settings()
