"""
Dependency Injection — Wires layers together
==============================================

Provides singleton-like access to services.
In production, use a proper DI container (e.g., Dependency Injector).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application import TaskService
    from app.infrastructure.queue import QueueManager

# Module-level singletons (set during app lifespan)
_task_service: TaskService | None = None
_queue_manager: QueueManager | None = None


def set_task_service(service: TaskService) -> None:
    global _task_service
    _task_service = service


def set_queue_manager(manager: QueueManager) -> None:
    global _queue_manager
    _queue_manager = manager


async def get_task_service() -> TaskService:
    if _task_service is None:
        raise RuntimeError("TaskService not initialized")
    return _task_service


async def get_queue_manager() -> QueueManager:
    if _queue_manager is None:
        raise RuntimeError("QueueManager not initialized")
    return _queue_manager
