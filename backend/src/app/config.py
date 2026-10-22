"""Async POC — Configuração centralizada."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Todas as configs em um lugar só. Override via env vars com prefixo POC_."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="POC_", case_sensitive=False)

    # App
    app_name: str = "Async POC"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Banco (SQLite async)
    db_url: str = "sqlite+aiosqlite:///./poc.db"

    # Queuefy
    queue_concurrency: int = 8

    # NiceGUI
    ui_prefix: str = "/ui"


@lru_cache
def get_settings() -> Settings:
    return Settings()
