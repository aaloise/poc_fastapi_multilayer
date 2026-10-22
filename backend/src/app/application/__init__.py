"""
Application Layer — Use Cases / Orchestrators
==============================================

Coordinates domain logic. Depends on domain ports, not infrastructure.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

import structlog

from app.domain import (
    Priority,
    Task,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
    TaskRepository,
    TaskResult,
    TaskStatus,
)

if TYPE_CHECKING:
    from app.infrastructure.queue import QueueManager

logger = structlog.get_logger()


class TaskService:
    """
    Orchestrates task creation, execution, and lifecycle.

    This is a *use case* — it knows WHAT to do but delegates HOW
    to the repository (port) and queue (infrastructure).
    """

    def __init__(
        self,
        repository: TaskRepository,
        queue_manager: QueueManager,
    ) -> None:
        self._repo = repository
        self._queue = queue_manager

    async def create_task(
        self,
        name: str,
        payload: dict | None = None,
        priority: Priority = Priority.MEDIUM,
        queue_name: str = "default",
    ) -> Task:
        """Create a new task and enqueue it for async execution."""
        task = Task(
            name=name,
            payload=payload or {},
            priority=priority,
            queue_name=queue_name,
        )

        # Persist
        task = await self._repo.save(task)

        # Enqueue via Queuefy
        await self._queue.enqueue(
            task_name=name,
            task_id=str(task.id),
            payload=task.payload,
            priority=queue_name,
        )

        # Domain event
        await logger.ainfo(
            "task.created",
            task_id=str(task.id),
            name=name,
            priority=priority.value,
        )

        return task

    async def execute_task(self, task_id: uuid.UUID) -> TaskResult:
        """Execute a task by its ID — called by Queuefy worker."""
        start = time.perf_counter()

        task = await self._repo.get_by_id(task_id)
        if task is None:
            return TaskResult(
                task_id=task_id,
                success=False,
                error="Task not found",
            )

        task.mark_running()
        await self._repo.save(task)

        try:
            # Simulate async work (replace with real logic)
            result = await self._process(task)

            task.mark_completed()
            await self._repo.save(task)

            duration = (time.perf_counter() - start) * 1000
            await logger.ainfo("task.completed", task_id=str(task_id), duration_ms=round(duration, 2))

            return TaskResult(
                task_id=task_id,
                success=True,
                output=result,
                duration_ms=duration,
            )

        except Exception as exc:
            task.mark_failed(str(exc))
            await self._repo.save(task)

            duration = (time.perf_counter() - start) * 1000
            await logger.aerror("task.failed", task_id=str(task_id), error=str(exc))

            return TaskResult(
                task_id=task_id,
                success=False,
                error=str(exc),
                duration_ms=duration,
            )

    async def _process(self, task: Task) -> dict:
        """
        Core processing logic. In a real app this would call
        external APIs, compute things, etc.
        """
        import asyncio
        await asyncio.sleep(0.1)  # Simulate I/O
        return {"processed": True, "task_name": task.name, "payload_size": len(task.payload)}

    async def get_task(self, task_id: uuid.UUID) -> Task | None:
        return await self._repo.get_by_id(task_id)

    async def list_tasks(
        self,
        status: TaskStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Task]:
        if status:
            return await self._repo.list_by_status(status)
        return await self._repo.list_all(limit=limit, offset=offset)

    async def get_stats(self) -> dict:
        """Get task statistics."""
        total = await self._repo.count()
        pending = len(await self._repo.list_by_status(TaskStatus.PENDING))
        running = len(await self._repo.list_by_status(TaskStatus.RUNNING))
        completed = len(await self._repo.list_by_status(TaskStatus.COMPLETED))
        failed = len(await self._repo.list_by_status(TaskStatus.FAILED))

        return {
            "total": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
        }
