"""
Configuração centralizada com suporte a múltiplos ambientes
============================================================

Ambientes suportados:
- development: SQLite local, debug habilitado
- production: PostgreSQL, otimizado para performance
- testing: SQLite em memória, para testes

Uso:
    POC_ENV=development uv run python -m app.main
    POC_ENV=production uv run python -m app.main
    POC_ENV=testing uv run pytest
"""

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


Environment = Literal["development", "production", "testing"]


class Settings(BaseSettings):
    """Configurações base — todas as environments herdam desta."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POC_",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App
    app_name: str = "Async POC"
    debug: bool = False
    environment: Environment = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    db_url: str = "sqlite+aiosqlite:///./poc.db"
    db_echo: bool = False
    
    # Queuefy
    queue_concurrency: int = 8
    
    # NiceGUI
    ui_prefix: str = "/ui"
    
    # Logging
    log_level: str = "INFO"


class DevSettings(Settings):
    """Configurações de desenvolvimento — SQLite local."""
    
    app_name: str = "Async POC (DEV)"
    debug: bool = True
    environment: Environment = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    db_url: str = "sqlite+aiosqlite:///./dev_poc.db"
    db_echo: bool = True
    queue_concurrency: int = 4
    log_level: str = "DEBUG"


class ProdSettings(Settings):
    """Configurações de produção — PostgreSQL."""
    
    app_name: str = "Async POC (PROD)"
    debug: bool = False
    environment: Environment = "production"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 8
    db_url: str = "postgresql+asyncpg://poc:poc@localhost:5432/poc_prod"
    db_echo: bool = False
    queue_concurrency: int = 16
    log_level: str = "WARNING"


class TestSettings(Settings):
    """Configurações de teste — SQLite em memória."""
    
    app_name: str = "Async POC (TEST)"
    debug: bool = True
    environment: Environment = "testing"
    db_url: str = "sqlite+aiosqlite:///:memory:"
    db_echo: bool = False
    queue_concurrency: int = 2
    log_level: str = "ERROR"


def get_settings() -> Settings:
    """Retorna configurações baseadas no ambiente."""
    import os
    env = os.getenv("POC_ENV", "development").lower()
    
    if env == "production":
        return ProdSettings()
    elif env == "testing":
        return TestSettings()
    else:
        return DevSettings()


@lru_cache
def get_cached_settings() -> Settings:
    """Retorna configurações cacheadas."""
    return get_settings()
