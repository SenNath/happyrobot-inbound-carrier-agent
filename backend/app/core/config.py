import json
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "HappyRobot Carrier Sales API"
    environment: Literal["local", "staging", "production", "test"] = "local"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/happyrobot"
    fmcsa_api_key: str = ""
    internal_api_key: str = "change-me"
    cors_origins: str | list[str] = ["http://localhost:3000"]
    allowed_hosts: str | list[str] = ["localhost", "127.0.0.1"]
    rate_limit_per_minute: int = 120
    seed_on_startup: bool = True
    force_https_redirect: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str) and value.startswith("["):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return list(value)

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str) and value.startswith("["):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        if isinstance(value, str):
            return [host.strip() for host in value.split(",") if host.strip()]
        return list(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
