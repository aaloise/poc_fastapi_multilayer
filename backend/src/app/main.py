"""Entry point — setup e lifespan."""

import asyncio
import sys
import platform
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# uvloop - não funciona no Windows
UVLOOP = False
if platform.system() != "Windows":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        UVLOOP = True
    except ImportError:
        pass

from app.config import get_settings
from app.database import init_db, close_db
from app.queue import init_queue, stop_queue
from app.routes import router

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown."""
    await logger.ainfo("starting", uvloop=UVLOOP, environment=settings.environment)

    # Startup
    await init_db(settings.db_url)
    await logger.ainfo("database.ready", url=settings.db_url)

    # Queuefy precisa do engine — vamos pegar do database module
    from app.database import _engine
    await init_queue(_engine, settings.queue_concurrency)
    await logger.ainfo("queue.ready")

    await logger.ainfo("started", host=settings.host, port=settings.port, environment=settings.environment)
    yield

    # Shutdown
    await stop_queue()
    await close_db()
    await logger.ainfo("stopped")


# FastAPI app
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

# Rota raiz - informações da API
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
    # Verifica argumento --env
    if "--env" in sys.argv:
        env_index = sys.argv.index("--env")
        if env_index + 1 < len(sys.argv):
            import os
            os.environ["POC_ENV"] = sys.argv[env_index + 1]
            # Recarrega settings
            from app.config import get_settings
            settings = get_settings()
    
    if "--granian" in sys.argv:
        from granian import Granian
        Granian("app.main:app", address=settings.host, port=settings.port, interface="asgi", workers=settings.workers).serve()
    else:
        import uvicorn
        uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug, loop="uvloop" if UVLOOP else "asyncio")
