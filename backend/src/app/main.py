"""
Async POC - FastAPI + Queuefy + NiceGUI
========================================

Ponto de entrada único para a aplicação.
Inicia API REST + Dashboard NiceGUI + Queue Worker.

Uso:
    uv run python -m app.main
"""

import asyncio
import platform
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from nicegui import ui, app as nicegui_app
import structlog

from app.config import get_settings
from app.database import init_db, close_db
from app.queue import init_queue, stop_queue
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida: startup e shutdown."""
    # Startup
    await logger.ainfo("starting", uvloop=UVLOOP, environment=settings.environment)
    
    await init_db(settings.db_url)
    await logger.ainfo("database.ready", url=settings.db_url)
    
    from app.database import _engine
    await init_queue(_engine, settings.queue_concurrency)
    await logger.ainfo("queue.ready")
    
    await logger.ainfo("started", host=settings.host, port=settings.port)
    
    yield
    
    # Shutdown
    await stop_queue()
    await close_db()
    await logger.ainfo("stopped")


# Configura NiceGUI app
nicegui_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
nicegui_app.include_router(router)


@nicegui_app.on_event("startup")
async def startup():
    """Inicializa banco e queue."""
    await logger.ainfo("starting", uvloop=UVLOOP, environment=settings.environment)
    
    await init_db(settings.db_url)
    await logger.ainfo("database.ready", url=settings.db_url)
    
    from app.database import _engine
    await init_queue(_engine, settings.queue_concurrency)
    await logger.ainfo("queue.ready")
    
    await logger.ainfo("started", host=settings.host, port=settings.port)


@nicegui_app.on_event("shutdown")
async def shutdown():
    """Finaliza banco e queue."""
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

# Inicia servidor
logger.info("nicegui.starting", prefix=settings.ui_prefix)

ui.run(
    title=settings.app_name,
    host=settings.host,
    port=settings.port,
    reload=settings.debug,
    show=False,
)
