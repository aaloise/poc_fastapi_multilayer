"""
Presentation Layer — FastAPI Routes
=====================================

HTTP API endpoints. Thin controllers — delegate to application services.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.domain import Priority, Task, TaskStatus

router = APIRouter(prefix="/api/v1", tags=["tasks"])


# ── Request / Response DTOs ──────────────────────────────────────────

class CreateTaskRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    payload: dict = Field(default_factory=dict)
    priority: Priority = Priority.MEDIUM
    queue_name: str = "default"


class TaskResponse(BaseModel):
    id: str
    name: str
    status: str
    priority: str
    queue_name: str
    attempts: int
    max_attempts: int
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None

    @classmethod
    def from_domain(cls, task: Task) -> TaskResponse:
        return cls(
            id=str(task.id),
            name=task.name,
            status=task.status,
            priority=task.priority,
            queue_name=task.queue_name,
            attempts=task.attempts,
            max_attempts=task.max_attempts,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            error=task.error,
        )


class StatsResponse(BaseModel):
    total: int
    pending: int
    running: int
    completed: int
    failed: int


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    components: dict[str, bool]


# ── Routes ───────────────────────────────────────────────────────────

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: CreateTaskRequest) -> TaskResponse:
    """Create a new task and enqueue it for async processing."""
    from app.dependencies import get_task_service

    service = await get_task_service()
    task = await service.create_task(
        name=request.name,
        payload=request.payload,
        priority=request.priority,
        queue_name=request.queue_name,
    )
    return TaskResponse.from_domain(task)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    status_filter: TaskStatus | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[TaskResponse]:
    """List tasks with optional status filter."""
    from app.dependencies import get_task_service

    service = await get_task_service()
    tasks = await service.list_tasks(status=status_filter, limit=limit, offset=offset)
    return [TaskResponse.from_domain(t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID) -> TaskResponse:
    """Get a task by ID."""
    from app.dependencies import get_task_service

    service = await get_task_service()
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_domain(task)


@router.get("/tasks/stats", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    """Get task statistics."""
    from app.dependencies import get_task_service

    service = await get_task_service()
    stats = await service.get_stats()
    return StatsResponse(**stats)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """System health check."""
    from app.infrastructure.prefect_flows import PREFECT_AVAILABLE

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
        components={
            "fastapi": True,
            "database": True,
            "queuefy": True,
            "prefect": PREFECT_AVAILABLE,
            "nicegui": True,
            "uvloop": True,
        },
    )


@router.post("/flows/data-pipeline")
async def run_data_pipeline(source: str = Query("api")) -> dict:
    """Trigger the Prefect data pipeline flow."""
    from app.infrastructure.prefect_flows import data_pipeline_flow, PREFECT_AVAILABLE

    if not PREFECT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Prefect not available")

    result = await data_pipeline_flow(source)
    return result


@router.post("/flows/batch")
async def run_batch(batch_size: int = Query(10, ge=1, le=100)) -> dict:
    """Trigger batch processing flow."""
    from app.infrastructure.prefect_flows import batch_processing_flow, PREFECT_AVAILABLE

    if not PREFECT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Prefect not available")

    result = await batch_processing_flow(batch_size)
    return result
