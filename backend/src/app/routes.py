"""FastAPI Routes — endpoints HTTP."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.models import Task, TaskStatus, Priority
from app.services import create_task, get_task_by_id, get_all_tasks, get_stats
from app.flows import data_pipeline, batch_process, PREFECT_OK
from app.parallel import parallel_map, heavy_computation

router = APIRouter(prefix="/api/v1", tags=["tasks"])


# ── DTOs ─────────────────────────────────────────────────────────────

class CreateTaskRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    payload: dict = Field(default_factory=dict)
    priority: Priority = Priority.MEDIUM


class TaskResponse(BaseModel):
    id: str
    name: str
    status: str
    priority: str
    queue: str
    attempts: int
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None

    @classmethod
    def from_task(cls, task: Task) -> "TaskResponse":
        return cls(
            id=str(task.id),
            name=task.name,
            status=task.status,
            priority=task.priority,
            queue=task.queue,
            attempts=task.attempts,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            error=task.error,
        )


# ── Routes ───────────────────────────────────────────────────────────

@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task_endpoint(req: CreateTaskRequest) -> TaskResponse:
    """Cria uma task e enfileira."""
    task = await create_task(name=req.name, payload=req.payload, priority=req.priority)
    return TaskResponse.from_task(task)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks_endpoint(
    status: TaskStatus | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> list[TaskResponse]:
    """Lista tasks."""
    tasks = await get_all_tasks(status=status, limit=limit)
    return [TaskResponse.from_task(t) for t in tasks]


@router.get("/tasks/stats", response_model=dict)
async def get_stats_endpoint() -> dict:
    """Estatísticas."""
    return await get_stats()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: uuid.UUID) -> TaskResponse:
    """Busca task por ID."""
    task = await get_task_by_id(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return TaskResponse.from_task(task)


@router.get("/health")
async def health_check() -> dict:
    """Health check."""
    from app.main import UVLOOP
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "fastapi": True,
            "database": True,
            "queuefy": True,
            "prefect": PREFECT_OK,
            "nicegui": True,
            "uvloop": UVLOOP,
        },
    }


@router.post("/flows/pipeline")
async def run_pipeline(source: str = Query("api")) -> dict:
    """Executa pipeline Prefect."""
    if not PREFECT_OK:
        raise HTTPException(503, "Prefect not available")
    return await data_pipeline(source)


@router.post("/flows/batch")
async def run_batch(size: int = Query(10, ge=1, le=100)) -> dict:
    """Executa batch process."""
    if not PREFECT_OK:
        raise HTTPException(503, "Prefect not available")
    return await batch_process(size)


@router.post("/parallel/compute")
async def run_parallel_computation(
    items: int = Query(100, ge=1, le=10000),
    n_jobs: int = Query(-1, ge=-1),
) -> dict:
    """
    Executa computação paralela com Joblib.
    
    Útil para tarefas CPU-bound (cálculos pesados, ML, etc).
    """
    import time
    start = time.perf_counter()
    
    # Executa computação pesada em paralelo
    results = await parallel_map(
        heavy_computation,
        list(range(items)),
        n_jobs=n_jobs,
    )
    
    duration = time.perf_counter() - start
    
    return {
        "items": items,
        "n_jobs": n_jobs,
        "results": len(results),
        "duration_seconds": round(duration, 3),
        "throughput": round(items / duration, 2),
    }
