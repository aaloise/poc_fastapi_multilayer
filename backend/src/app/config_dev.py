"""
Ambiente de Desenvolvimento — SQLite local
===========================================

Configuração para desenvolvimento com SQLite.
Banco criado automaticamente no diretório local.

Uso:
    uv run python -m app.main --env dev
    # ou
    POC_ENV=development uv run python -m app.main
"""

from app.config import Settings


class DevSettings(Settings):
    """Configurações de desenvolvimento."""
    
    # App
    app_name: str = "Async POC (DEV)"
    debug: bool = True
    environment: str = "development"
    
    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Database — SQLite local
    db_url: str = "sqlite+aiosqlite:///./dev_poc.db"
    db_echo: bool = True  # Mostra SQL no console
    
    # Queuefy
    queue_concurrency: int = 4  # Menos workers em dev
    
    # NiceGUI
    ui_prefix: str = "/ui"
    
    # Logging
    log_level: str = "DEBUG"


def get_dev_settings() -> DevSettings:
    """Retorna configurações de desenvolvimento."""
    return DevSettings()
