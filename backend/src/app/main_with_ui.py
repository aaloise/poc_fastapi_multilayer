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
from fastapi import FastAPI
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


# Cria o FastAPI app
fastapi_app = FastAPI(title=settings.app_name, version="0.1.0")
fastapi_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
fastapi_app.include_router(router)


# Rota raiz - redireciona para o dashboard
@fastapi_app.get("/")
async def root():
    """Redireciona para o dashboard."""
    return RedirectResponse(url="/ui/")


# Configura as páginas do NiceGUI
setup_ui(settings.ui_prefix)

logger.info("nicegui.pages.registered", prefix=settings.ui_prefix)


# Startup e shutdown
@fastapi_app.on_event("startup")
async def startup():
    """Inicializa banco e queue."""
    await logger.ainfo("starting", uvloop=UVLOOP, environment=settings.environment)
    
    await init_db(settings.db_url)
    await logger.ainfo("database.ready", url=settings.db_url)
    
    from app.database import _engine
    await init_queue(_engine, settings.queue_concurrency)
    await logger.ainfo("queue.ready")
    
    await logger.ainfo("started", host=settings.host, port=settings.port)


@fastapi_app.on_event("shutdown")
async def shutdown():
    """Finaliza banco e queue."""
    await stop_queue()
    await close_db()
    await logger.ainfo("stopped")


if __name__ == "__main__":
    # Inicia com NiceGUI
    ui.run(
        title=settings.app_name,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        show=False,
        fastapi_app=fastapi_app,
    )
