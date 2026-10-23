"""Serviços — lógica de negócio."""

import uuid
from datetime import datetime, timezone

import structlog

from app.database import get_session
from app.models import Task, TaskStatus, Priority, save_task, get_task, list_tasks, count_tasks

logger = structlog.get_logger()


async def create_task(name: str, payload: dict | None = None, priority: Priority = Priority.MEDIUM) -> Task:
    """Cria uma nova task."""
    task = Task(name=name, payload=payload or {}, priority=priority)

    session = await get_session()
    async with session:
        task = await save_task(session, task)

    await logger.ainfo("task.created", task_id=str(task.id), name=name)
    return task


async def execute_task(task_id: uuid.UUID) -> dict:
    """Executa uma task (chamado pelo worker do Queuefy)."""
    session = await get_session()
    async with session:
        task = await get_task(session, task_id)
        if not task:
            return {"success": False, "error": "Task not found"}

        # Mark as running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        task.attempts += 1
        await save_task(session, task)

        # Process (simula trabalho async)
        import asyncio
        await asyncio.sleep(0.1)

        # Mark as completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        await save_task(session, task)

    await logger.ainfo("task.completed", task_id=str(task_id))
    return {"success": True, "task_id": str(task_id)}


async def get_task_by_id(task_id: uuid.UUID) -> Task | None:
    """Busca task por ID."""
    session = await get_session()
    async with session:
        return await get_task(session, task_id)


async def get_all_tasks(status: TaskStatus | None = None, limit: int = 50) -> list[Task]:
    """Lista tasks."""
    session = await get_session()
    async with session:
        return await list_tasks(session, status=status, limit=limit)


async def get_stats() -> dict:
    """Estatísticas de tasks."""
    session = await get_session()
    async with session:
        return await count_tasks(session)
