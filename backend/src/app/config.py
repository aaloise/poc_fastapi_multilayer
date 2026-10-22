"""Application settings — loaded from env vars / .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised configuration. All values can be overridden via env vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="POC_",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────────────────
    app_name: str = "Async POC"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # ── Server ───────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # ── Database (async SQLAlchemy) ──────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./poc.db"
    database_echo: bool = False

    # ── Queuefy ──────────────────────────────────────────────────────
    queue_store: Literal["sqlalchemy", "redis", "memory"] = "sqlalchemy"
    queue_redis_url: str = "redis://localhost:6379/0"
    queue_concurrency: int = 8

    # ── Prefect ──────────────────────────────────────────────────────
    prefect_api_url: str = "http://localhost:4200/api"
    prefect_enabled: bool = True

    # ── NiceGUI ──────────────────────────────────────────────────────
    nicegui_prefix: str = "/ui"
    nicegui_title: str = "Async POC Dashboard"

    # ── Paths ────────────────────────────────────────────────────────
    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @property
    def db_path(self) -> Path:
        return self.base_dir / "poc.db"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings singleton."""
    return Settings()
