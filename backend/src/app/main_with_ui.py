"""
Entry point com NiceGUI integrado
==================================

Este arquivo inicia a aplicação com NiceGUI integrado.
Use este arquivo para ter o dashboard visual.

Uso:
    uv run python -m app.main_with_ui
"""

import asyncio
import sys
import platform

# uvloop - não funciona no Windows
UVLOOP = False
if platform.system() != "Windows":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        UVLOOP = True
    except ImportError:
        pass

from nicegui import ui, app as nicegui_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.database import init_db, close_db
from app.queue import init_queue, stop_queue
from app.routes import router
from app.ui import setup_ui

import structlog

settings = get_settings()
logger = structlog.get_logger()


# Configura o app do NiceGUI
nicegui_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
nicegui_app.include_router(router)


# Startup event
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


# Shutdown event
@nicegui_app.on_event("shutdown")
async def shutdown():
    """Finaliza banco e queue."""
    await stop_queue()
    await close_db()
    await logger.ainfo("stopped")


# Rota raiz - redireciona para o dashboard
@nicegui_app.get("/")
async def root():
    """Redireciona para o dashboard."""
    return RedirectResponse(url="/ui/")


# Configura as páginas do NiceGUI
setup_ui(settings.ui_prefix)

logger.info("nicegui.pages.registered", prefix=settings.ui_prefix)


if __name__ == "__main__":
    logger.info("nicegui.starting", prefix=settings.ui_prefix)
    
    # Inicia o servidor NiceGUI
    ui.run(
        title=settings.app_name,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        show=False,
    )
