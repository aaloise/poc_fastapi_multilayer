"""Entry point — setup e lifespan."""

import asyncio
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# uvloop
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    UVLOOP = True
except ImportError:
    UVLOOP = False

from app.config import get_settings
from app.database import init_db, close_db
from app.queue import init_queue, stop_queue
from app.routes import router

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown."""
    await logger.ainfo("starting", uvloop=UVLOOP)

    # Startup
    await init_db(settings.db_url)
    await logger.ainfo("database.ready")

    # Queuefy precisa do engine — vamos pegar do database module
    from app.database import _engine
    await init_queue(_engine, settings.queue_concurrency)
    await logger.ainfo("queue.ready")

    # NiceGUI
    try:
        from nicegui import ui
        from app.ui import setup_ui
        setup_ui(settings.ui_prefix)
        ui.run(title="Async POC", port=settings.port, reload=settings.debug, show=False, fastapi_app=app)
        await logger.ainfo("ui.ready", prefix=settings.ui_prefix)
    except Exception as e:
        await logger.awarning("ui.error", error=str(e))

    await logger.ainfo("started", host=settings.host, port=settings.port)
    yield

    # Shutdown
    await stop_queue()
    await close_db()
    await logger.ainfo("stopped")


# FastAPI app
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


if __name__ == "__main__":
    if "--granian" in sys.argv:
        from granian import Granian
        Granian("app.main:app", address=settings.host, port=settings.port, interface="asgi", workers=4).serve()
    else:
        import uvicorn
        uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug, loop="uvloop" if UVLOOP else "asyncio")
