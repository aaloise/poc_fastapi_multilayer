"""
Infrastructure Layer — Database (Async SQLAlchemy)
====================================================
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import JSON, DateTime, Enum, Integer, String, select, func, delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain import Priority, Task, TaskRepository, TaskStatus


# ── SQLAlchemy Models ────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class TaskModel(Base):
    """SQLAlchemy model for Task entity."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, index=True
    )
    priority: Mapped[str] = mapped_column(
        Enum(Priority), default=Priority.MEDIUM
    )
    queue_name: Mapped[str] = mapped_column(String(100), default="default")
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    def to_domain(self) -> Task:
        return Task(
            id=uuid.UUID(self.id),
            name=self.name,
            payload=self.payload or {},
            status=TaskStatus(self.status),
            priority=Priority(self.priority),
            queue_name=self.queue_name,
            max_attempts=self.max_attempts,
            attempts=self.attempts,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            error=self.error,
        )

    @classmethod
    def from_domain(cls, task: Task) -> TaskModel:
        return TaskModel(
            id=str(task.id),
            name=task.name,
            payload=task.payload,
            status=task.status,
            priority=task.priority,
            queue_name=task.queue_name,
            max_attempts=task.max_attempts,
            attempts=task.attempts,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error=task.error,
        )


# ── Engine & Session Factory ─────────────────────────────────────────

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_database(database_url: str, echo: bool = False) -> AsyncEngine:
    """Initialize the async database engine and create tables."""
    global _engine, _session_factory

    _engine = create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
    )

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with _session_factory() as session:
        yield session


async def close_database() -> None:
    """Dispose the engine and close all connections."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None


# ── Repository Adapter ───────────────────────────────────────────────

class SQLAlchemyTaskRepository(TaskRepository):
    """Infrastructure adapter implementing the domain repository port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, task: Task) -> Task:
        model = TaskModel.from_domain(task)
        existing = await self._session.get(TaskModel, str(task.id))
        if existing:
            for key, value in model.__dict__.items():
                if not key.startswith("_"):
                    setattr(existing, key, value)
        else:
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model.to_domain()

    async def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        model = await self._session.get(TaskModel, str(task_id))
        return model.to_domain() if model else None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Task]:
        stmt = select(TaskModel).offset(offset).limit(limit).order_by(TaskModel.created_at.desc())
        result = await self._session.execute(stmt)
        return [row.to_domain() for row in result.scalars().all()]

    async def list_by_status(self, status: TaskStatus) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.status == status).order_by(TaskModel.created_at.desc())
        result = await self._session.execute(stmt)
        return [row.to_domain() for row in result.scalars().all()]

    async def delete(self, task_id: uuid.UUID) -> bool:
        stmt = delete(TaskModel).where(TaskModel.id == str(task_id))
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def count(self) -> int:
        stmt = select(func.count()).select_from(TaskModel)
        result = await self._session.execute(stmt)
        return result.scalar_one()
