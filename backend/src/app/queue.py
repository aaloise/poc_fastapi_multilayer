"""Queuefy — fila de tarefas async."""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine
from queuefy.app import Queuefy
from queuefy.store.sqlalchemy import SqlAlchemyStore
from queuefy.worker import Worker

logger = structlog.get_logger()

# Queue global
_queuefy: Queuefy | None = None
_worker: Worker | None = None


async def init_queue(engine: AsyncEngine, concurrency: int = 8) -> None:
    """Inicializa Queuefy e registra handlers."""
    global _queuefy, _worker

    _queuefy = Queuefy(SqlAlchemyStore(engine))
    await _queuefy.setup()

    # Registra handlers
    @_queuefy.task("process_task", max_attempts=3, timeout=60)
    async def handle_process_task(task_id: str, payload: dict) -> dict:
        from app.services import execute_task
        return await execute_task(uuid.UUID(task_id))

    @_queuefy.task("send_notification", max_attempts=5, timeout=30)
    async def handle_notification(task_id: str, message: str, channel: str) -> dict:
        import asyncio
        await asyncio.sleep(0.05)
        await logger.ainfo("notification.sent", task_id=task_id, channel=channel)
        return {"sent": True, "channel": channel}

    @_queuefy.task("daily_report", cron="0 4 * * *")
    async def handle_report() -> dict:
        from app.services import get_stats
        stats = await get_stats()
        await logger.ainfo("report.generated", stats=stats)
        return {"report": stats}

    # Inicia worker em background
    import asyncio
    _worker = Worker(_queuefy, concurrency=concurrency)
    asyncio.create_task(_worker.run())

    await logger.ainfo("queue.started", concurrency=concurrency)


async def enqueue(task_name: str, task_id: str | None = None, **kwargs) -> str:
    """Enfileira uma task."""
    if not _queuefy:
        raise RuntimeError("Queue não inicializada")

    tid = task_id or str(uuid.uuid4())
    await _queuefy.enqueue(task_name, task_id=tid, **kwargs)
    await logger.ainfo("task.enqueued", task_name=task_name, task_id=tid)
    return tid


async def stop_queue() -> None:
    """Para o worker."""
    global _worker
    if _worker:
        await logger.ainfo("queue.stopped")
        _worker = None
