"""
Domain Layer — Entities, Value Objects & Repository Ports
==========================================================

This layer has ZERO dependencies on infrastructure.
It defines *what* the system does, not *how*.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field


# ── Value Objects ────────────────────────────────────────────────────

class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Entities ─────────────────────────────────────────────────────────

class Task(BaseModel):
    """Core domain entity — represents a unit of work."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    payload: dict = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    queue_name: str = "default"
    max_attempts: int = 3
    attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None

    class Config:
        use_enum_values = True

    @property
    def is_terminal(self) -> bool:
        return self.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)

    def mark_running(self) -> None:
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.attempts += 1

    def mark_completed(self) -> None:
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()


class TaskResult(BaseModel):
    """Result of a task execution."""

    task_id: uuid.UUID
    success: bool
    output: dict | None = None
    error: str | None = None
    duration_ms: float = 0.0


# ── Domain Events ────────────────────────────────────────────────────

class TaskCreated(BaseModel):
    task_id: uuid.UUID
    name: str
    priority: Priority


class TaskCompleted(BaseModel):
    task_id: uuid.UUID
    name: str
    duration_ms: float


class TaskFailed(BaseModel):
    task_id: uuid.UUID
    name: str
    error: str


# ── Repository Ports (interfaces) ────────────────────────────────────

class TaskRepository(Protocol):
    """Port — infrastructure provides the adapter."""

    async def save(self, task: Task) -> Task: ...
    async def get_by_id(self, task_id: uuid.UUID) -> Task | None: ...
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Task]: ...
    async def list_by_status(self, status: TaskStatus) -> list[Task]: ...
    async def delete(self, task_id: uuid.UUID) -> bool: ...
    async def count(self) -> int: ...
