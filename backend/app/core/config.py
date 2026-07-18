from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Customer Development System"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/customer_dev"
    redis_url: str = "redis://localhost:6379/0"
    frontend_origin: str = "http://localhost:3000"
    crawl_user_agent: str = "CustomerDevelopmentBot/0.1 (+contact@example.com)"
    crawl_timeout_seconds: float = 12.0
    crawl_min_domain_delay_seconds: float = 1.0
    search_provider: str = "demo"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-terra"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("frontend_origin")
    @classmethod
    def normalize_frontend_origin(cls, value: str) -> str:
        if value and not value.startswith(("http://", "https://")):
            return f"https://{value}"
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
