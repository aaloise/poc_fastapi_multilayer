"""
Async POC - FastAPI + Queuefy + NiceGUI
========================================

Entry point único que inicia:
- API REST (FastAPI)
- Dashboard (NiceGUI)
- Task Queue (Queuefy)
- Database (SQLAlchemy)

Todos compartilham os mesmos services, sem HTTP entre eles.

Uso:
    uv run python -m app.main
"""

import asyncio
import platform

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from nicegui import ui, app as nicegui_app
import structlog

from app.config import get_settings
from app.database import init_db, close_db
from app.queue import init_queue, stop_queue
from app.parallel import init_parallel, shutdown_parallel
from app.routes import router
from app.ui import setup_ui

# uvloop - não funciona no Windows
UVLOOP = False
if platform.system() != "Windows":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        UVLOOP = True
    except ImportError:
        pass

settings = get_settings()
logger = structlog.get_logger()


# Configura NiceGUI app
nicegui_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Adiciona rotas da API ao NiceGUI
nicegui_app.include_router(router)


# Startup event - inicializa banco, queue e parallel
@nicegui_app.on_event("startup")
async def startup_event():
    """Inicializa banco, queue e parallel no startup."""
    await logger.ainfo("starting", uvloop=UVLOOP, environment=settings.environment)
    
    await init_db(settings.db_url)
    await logger.ainfo("database.ready", url=settings.db_url)
    
    from app.database import _engine
    await init_queue(_engine, settings.queue_concurrency)
    await logger.ainfo("queue.ready")
    
    init_parallel(n_jobs=-1)  # Usa todos os cores disponíveis
    await logger.ainfo("parallel.ready")
    
    await logger.ainfo("started", host=settings.host, port=settings.port)


# Shutdown event - finaliza banco, queue e parallel
@nicegui_app.on_event("shutdown")
async def shutdown_event():
    """Finaliza banco, queue e parallel no shutdown."""
    shutdown_parallel()
    await stop_queue()
    await close_db()
    await logger.ainfo("stopped")


# Rota raiz - redireciona para dashboard
@nicegui_app.get("/")
async def root():
    """Redireciona para o dashboard."""
    return RedirectResponse(url="/ui/")


# Configura páginas NiceGUI
setup_ui(settings.ui_prefix)

logger.info("nicegui.pages.registered", prefix=settings.ui_prefix)
logger.info("nicegui.starting", prefix=settings.ui_prefix)

# Inicia servidor NiceGUI (com FastAPI integrado)
ui.run(
    title=settings.app_name,
    host=settings.host,
    port=settings.port,
    reload=settings.debug,
    show=False,
)
