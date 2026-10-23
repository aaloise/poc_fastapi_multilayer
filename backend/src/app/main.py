"""
Async POC - API REST (sem UI)
==============================

Entry point para API REST pura (sem NiceGUI).
Use este arquivo quando quiser apenas a API.

Uso:
    uv run python -m app.main
"""

import asyncio
import platform
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import get_settings
from app.database import init_db, close_db
from app.queue import init_queue, stop_queue
from app.routes import router

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


# Cria FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Rotas da API
app.include_router(router)


# Rota raiz
@app.get("/")
async def root():
    """Informações da API."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "api": "/api/v1/",
        "dashboard": "Execute: uv run python -m app.main_with_ui",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        loop="uvloop" if UVLOOP else "asyncio",
    )
