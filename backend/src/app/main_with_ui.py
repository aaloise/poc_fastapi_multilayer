"""
Async POC - API REST + Dashboard NiceGUI
=========================================

Entry point para API REST com Dashboard NiceGUI integrado.
Use este arquivo quando quiser API + UI visual.

Uso:
    uv run python -m app.main_with_ui
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


# Configura NiceGUI app (integra com FastAPI)
nicegui_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Adiciona rotas da API ao NiceGUI
nicegui_app.include_router(router)

# Configura lifespan do NiceGUI
nicegui_app.router.lifespan_context = lifespan


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
