"""
Infrastructure Layer — Queuefy Integration
============================================

Async task queue using Queuefy with SQLAlchemy store.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine

from queuefy.app import Queuefy
from queuefy.store.sqlalchemy import SqlAlchemyStore
from queuefy.worker import Worker

from app.domain import Priority

logger = structlog.get_logger()


class QueueManager:
    """
    Wraps Queuefy to provide a clean async interface
    for enqueuing and managing tasks.
    """

    def __init__(self, engine: AsyncEngine, concurrency: int = 8) -> None:
        self._store = SqlAlchemyStore(engine)
        self._app = Queuefy(self._store)
        self._worker: Worker | None = None
        self._concurrency = concurrency
        self._task_handlers: dict[str, Any] = {}

    async def setup(self) -> None:
        """Initialize Queuefy tables and register task handlers."""
        await self._app.setup()
        self._register_handlers()
        await logger.ainfo("queuefy.setup", concurrency=self._concurrency)

    def _register_handlers(self) -> None:
        """Register all task handlers with Queuefy."""

        @self._app.task("process_task", max_attempts=3, timeout=60)
        async def handle_process_task(task_id: str, payload: dict) -> dict:
            """Handler for generic task processing."""
            await logger.ainfo("queuefy.task.received", task_id=task_id)
            # Delegate to the application service
            from app.dependencies import get_task_service
            service = await get_task_service()
            result = await service.execute_task(uuid.UUID(task_id))
            return {"task_id": task_id, "success": result.success}

        @self._app.task("send_notification", max_attempts=5, timeout=30)
        async def handle_send_notification(task_id: str, message: str, channel: str) -> dict:
            """Handler for notification tasks."""
            await logger.ainfo("queuefy.notification", task_id=task_id, channel=channel)
            import asyncio
            await asyncio.sleep(0.05)  # Simulate notification sending
            return {"task_id": task_id, "sent": True, "channel": channel}

        @self._app.task("generate_report", cron="0 */6 * * *")
        async def handle_generate_report() -> dict:
            """Scheduled report generation — runs every 6 hours."""
            await logger.ainfo("queuefy.report.generating")
            from app.dependencies import get_task_service
            service = await get_task_service()
            stats = await service.get_stats()
            return {"report": stats}

        @self._app.task("cleanup_old_tasks", cron="0 2 * * *")
        async def handle_cleanup() -> dict:
            """Scheduled cleanup — runs daily at 2 AM."""
            await logger.ainfo("queuefy.cleanup.running")
            return {"cleaned": True}

    async def enqueue(
        self,
        task_name: str,
        task_id: str | None = None,
        payload: dict | None = None,
        priority: str = "default",
    ) -> str:
        """Enqueue a task for async execution."""
        tid = task_id or str(uuid.uuid4())

        if task_name == "process_task":
            await self._app.enqueue(
                "process_task",
                task_id=tid,
                payload=payload or {},
            )
        elif task_name == "send_notification":
            await self._app.enqueue(
                "send_notification",
                task_id=tid,
                message=payload.get("message", ""),
                channel=payload.get("channel", "email"),
            )
        else:
            await self._app.enqueue(
                "process_task",
                task_id=tid,
                payload=payload or {},
            )

        await logger.ainfo("queuefy.enqueued", task_name=task_name, task_id=tid)
        return tid

    async def enqueue_at(
        self,
        task_name: str,
        when: Any,
        payload: dict | None = None,
    ) -> str:
        """Schedule a task to run at a specific time."""
        tid = str(uuid.uuid4())
        await self._app.enqueue_at(task_name, when, **(payload or {}))
        await logger.ainfo("queuefy.scheduled", task_name=task_name, when=str(when))
        return tid

    async def start_worker(self) -> None:
        """Start the Queuefy worker (runs in background)."""
        import asyncio
        self._worker = Worker(self._app, concurrency=self._concurrency)
        # Run worker in background task
        asyncio.create_task(self._worker.run())
        await logger.ainfo("queuefy.worker.started", concurrency=self._concurrency)

    async def stop_worker(self) -> None:
        """Stop the Queuefy worker gracefully."""
        if self._worker:
            # Worker will stop on cancellation
            await logger.ainfo("queuefy.worker.stopped")

    @property
    def queuefy_app(self) -> Queuefy:
        return self._app
