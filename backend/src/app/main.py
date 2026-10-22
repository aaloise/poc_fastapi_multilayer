"""
Main Application Entry Point
==============================

Wires all layers together:
  1. FastAPI app with async lifespan
  2. Granian ASGI server with uvloop
  3. Queuefy task queue
  4. NiceGUI pages
  5. Prefect flows (optional)

Run with:
  python -m app.main
  # or
  granian --interface asgi --config granian.toml app.main:app
"""

from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Try uvloop — fall back gracefully
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

from app.config import get_settings
from app.dependencies import set_queue_manager, set_task_service
from app.infrastructure.database import (
    SQLAlchemyTaskRepository,
    close_database,
    get_session,
    init_database,
)
from app.infrastructure.queue import QueueManager
from app.application import TaskService
from app.presentation.api import router as api_router

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async lifespan — startup and shutdown.

    Startup order:
      1. Database (SQLAlchemy async)
      2. Queuefy (task queue)
      3. Wire dependencies
      4. Start Queuefy worker
      5. Mount NiceGUI

    Shutdown order (reverse):
      1. Stop Queuefy worker
      2. Close database
    """
    await logger.ainfo("app.starting", uvloop=UVLOOP_AVAILABLE)

    # ── Startup ──────────────────────────────────────────────────────

    # 1. Database
    engine = await init_database(
        database_url=settings.database_url,
        echo=settings.database_echo,
    )
    await logger.ainfo("database.connected", url=settings.database_url)

    # 2. Queuefy
    queue_manager = QueueManager(
        engine=engine,
        concurrency=settings.queue_concurrency,
    )
    await queue_manager.setup()
    await logger.ainfo("queuefy.initialized")

    # 3. Wire dependencies
    set_queue_manager(queue_manager)

    # Create TaskService with repository
    async for session in get_session():
        repository = SQLAlchemyTaskRepository(session)
        task_service = TaskService(
            repository=repository,
            queue_manager=queue_manager,
        )
        set_task_service(task_service)
        break

    # 4. Start Queuefy worker
    await queue_manager.start_worker()
    await logger.ainfo("queuefy.worker.running")

    # 5. Mount NiceGUI
    try:
        from nicegui import ui
        from app.presentation.ui import setup_nicegui_pages

        setup_nicegui_pages(prefix=settings.nicegui_prefix)
        ui.run(
            title=settings.nicegui_title,
            port=settings.port,
            reload=settings.debug,
            show=False,
            fastapi_app=app,
        )
        await logger.ainfo("nicegui.mounted", prefix=settings.nicegui_prefix)
    except Exception as e:
        await logger.awarning("nicegui.error", error=str(e))

    await logger.ainfo(
        "app.started",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        uvloop=UVLOOP_AVAILABLE,
    )

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    await logger.ainfo("app.shutting_down")
    await queue_manager.stop_worker()
    await close_database()
    await logger.ainfo("app.stopped")


# ── FastAPI Application ──────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="POC: FastAPI + uvloop + Granian + Prefect + Queuefy + NiceGUI",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)


# ── Direct execution ─────────────────────────────────────────────────

def main():
    """Run with Granian ASGI server."""
    from granian import Granian

    server = Granian(
        "app.main:app",
        address=settings.host,
        port=settings.port,
        interface="asgi",
        workers=settings.workers,
        threads=2,
        http="auto",
        log_level="info",
    )
    server.serve()


if __name__ == "__main__":
    if "--granian" in sys.argv:
        main()
    else:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            loop="uvloop" if UVLOOP_AVAILABLE else "asyncio",
        )
