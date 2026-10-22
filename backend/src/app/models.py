"""Modelos de domínio e persistência — tudo junto, simples."""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, Enum, Integer, String, select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ── Enums ────────────────────────────────────────────────────────────

class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Modelo de Domínio (o que a aplicação usa) ────────────────────────

class Task(BaseModel):
    """Task — a entidade principal."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    payload: dict = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    queue: str = "default"
    attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


# ── Modelo de Banco (SQLAlchemy) ─────────────────────────────────────

class Base(DeclarativeBase):
    pass


class TaskRow(Base):
    """Linha na tabela tasks."""
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority: Mapped[str] = mapped_column(Enum(Priority), default=Priority.MEDIUM)
    queue: Mapped[str] = mapped_column(String(100), default="default")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    def to_task(self) -> Task:
        return Task(
            id=uuid.UUID(self.id),
            name=self.name,
            payload=self.payload or {},
            status=TaskStatus(self.status),
            priority=Priority(self.priority),
            queue=self.queue,
            attempts=self.attempts,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            error=self.error,
        )

    @classmethod
    def from_task(cls, task: Task) -> "TaskRow":
        return TaskRow(
            id=str(task.id),
            name=task.name,
            payload=task.payload,
            status=task.status,
            priority=task.priority,
            queue=task.queue,
            attempts=task.attempts,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error=task.error,
        )


# ── Operações de Banco (funções async simples) ──────────────────────

async def save_task(session: AsyncSession, task: Task) -> Task:
    """Salva ou atualiza uma task."""
    row = TaskRow.from_task(task)
    existing = await session.get(TaskRow, str(task.id))
    if existing:
        for k, v in row.__dict__.items():
            if not k.startswith("_"):
                setattr(existing, k, v)
    else:
        session.add(row)
    await session.commit()
    await session.refresh(row if existing else row)
    return (existing or row).to_task()


async def get_task(session: AsyncSession, task_id: uuid.UUID) -> Task | None:
    """Busca task por ID."""
    row = await session.get(TaskRow, str(task_id))
    return row.to_task() if row else None


async def list_tasks(session: AsyncSession, status: TaskStatus | None = None, limit: int = 50) -> list[Task]:
    """Lista tasks, opcionalmente filtrando por status."""
    stmt = select(TaskRow).order_by(TaskRow.created_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(TaskRow.status == status)
    result = await session.execute(stmt)
    return [r.to_task() for r in result.scalars().all()]


async def count_tasks(session: AsyncSession) -> dict:
    """Conta tasks por status."""
    total = (await session.execute(select(func.count()).select_from(TaskRow))).scalar_one()
    pending = (await session.execute(
        select(func.count()).select_from(TaskRow).where(TaskRow.status == TaskStatus.PENDING)
    )).scalar_one()
    running = (await session.execute(
        select(func.count()).select_from(TaskRow).where(TaskRow.status == TaskStatus.RUNNING)
    )).scalar_one()
    completed = (await session.execute(
        select(func.count()).select_from(TaskRow).where(TaskRow.status == TaskStatus.COMPLETED)
    )).scalar_one()
    failed = (await session.execute(
        select(func.count()).select_from(TaskRow).where(TaskRow.status == TaskStatus.FAILED)
    )).scalar_one()
    return {"total": total, "pending": pending, "running": running, "completed": completed, "failed": failed}
