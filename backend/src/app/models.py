"""
Modelos — Domain + Banco de Dados
==================================

Este arquivo contém:
1. Modelos de domínio (Pydantic) — o que a aplicação usa
2. Modelos de banco (SQLAlchemy) — as tabelas no SQLite/PostgreSQL
3. Funções de acesso ao banco (CRUD async)

Tabelas criadas no banco:
- tasks: armazena as tasks da aplicação
- queuefy_runs: tabelas internas do Queuefy (criadas automaticamente)
- queuefy_schedules: agendamentos do Queuefy (criadas automaticamente)
"""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, Enum, Integer, String, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ── Enums ────────────────────────────────────────────────────────────

class TaskStatus(StrEnum):
    """Status de uma task."""
    PENDING = "pending"      # Criada, aguardando processamento
    RUNNING = "running"      # Sendo processada pelo worker
    COMPLETED = "completed"  # Processada com sucesso
    FAILED = "failed"        # Falhou (pode ter retry)


class Priority(StrEnum):
    """Prioridade da task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Modelo de Domínio (Pydantic) ─────────────────────────────────────

class Task(BaseModel):
    """
    Task — entidade principal da aplicação.
    
    Este é o modelo que a aplicação usa internamente.
    Não é o modelo do banco, mas sim o "objeto de negócio".
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str                                    # Nome da task (ex: "send_email")
    payload: dict = Field(default_factory=dict)  # Dados da task (JSON)
    status: TaskStatus = TaskStatus.PENDING      # Status atual
    priority: Priority = Priority.MEDIUM         # Prioridade
    queue: str = "default"                       # Fila (para organização)
    attempts: int = 0                            # Quantas vezes tentou processar
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None           # Quando começou a processar
    completed_at: datetime | None = None         # Quando terminou
    error: str | None = None                     # Mensagem de erro (se falhou)


# ── Modelo de Banco (SQLAlchemy) ─────────────────────────────────────

class Base(DeclarativeBase):
    """Base para todos os modelos SQLAlchemy."""
    pass


class TaskRow(Base):
    """
    Tabela 'tasks' no banco de dados.
    
    CREATE TABLE tasks (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        payload JSON,
        status VARCHAR(20) DEFAULT 'pending',
        priority VARCHAR(20) DEFAULT 'medium',
        queue VARCHAR(100) DEFAULT 'default',
        attempts INTEGER DEFAULT 0,
        created_at DATETIME,
        started_at DATETIME,
        completed_at DATETIME,
        error VARCHAR(1000)
    );
    
    CREATE INDEX ix_tasks_name ON tasks(name);
    CREATE INDEX ix_tasks_status ON tasks(status);
    """
    __tablename__ = "tasks"

    # Colunas
    id: Mapped[str] = mapped_column(String(36), primary_key=True, comment="UUID da task")
    name: Mapped[str] = mapped_column(String(255), index=True, comment="Nome da task")
    payload: Mapped[dict] = mapped_column(JSON, default=dict, comment="Dados da task (JSON)")
    status: Mapped[str] = mapped_column(
        Enum(TaskStatus), 
        default=TaskStatus.PENDING, 
        index=True,
        comment="Status: pending/running/completed/failed"
    )
    priority: Mapped[str] = mapped_column(
        Enum(Priority), 
        default=Priority.MEDIUM,
        comment="Prioridade: low/medium/high/critical"
    )
    queue: Mapped[str] = mapped_column(String(100), default="default", comment="Nome da fila")
    attempts: Mapped[int] = mapped_column(Integer, default=0, comment="Número de tentativas")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="Quando foi criada")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="Quando começou a processar")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="Quando terminou")
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True, comment="Mensagem de erro")

    # Conversão: TaskRow (banco) → Task (domínio)
    def to_task(self) -> Task:
        """Converte a linha do banco para o modelo de domínio."""
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

    # Conversão: Task (domínio) → TaskRow (banco)
    @classmethod
    def from_task(cls, task: Task) -> "TaskRow":
        """Converte o modelo de domínio para uma linha do banco."""
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


# ── Operações de Banco (CRUD Async) ──────────────────────────────────

async def save_task(session: AsyncSession, task: Task) -> Task:
    """
    Salva ou atualiza uma task no banco.
    
    Se a task já existe (mesmo ID), atualiza.
    Se não existe, insere nova linha.
    """
    row = TaskRow.from_task(task)
    
    # Verifica se já existe
    existing = await session.get(TaskRow, str(task.id))
    
    if existing:
        # Atualiza campos
        for k, v in row.__dict__.items():
            if not k.startswith("_"):
                setattr(existing, k, v)
    else:
        # Insere nova linha
        session.add(row)
    
    await session.commit()
    await session.refresh(row if existing else row)
    
    return (existing or row).to_task()


async def get_task(session: AsyncSession, task_id: uuid.UUID) -> Task | None:
    """Busca uma task por ID."""
    row = await session.get(TaskRow, str(task_id))
    return row.to_task() if row else None


async def list_tasks(
    session: AsyncSession, 
    status: TaskStatus | None = None, 
    limit: int = 50
) -> list[Task]:
    """
    Lista tasks, opcionalmente filtrando por status.
    
    Exemplos:
        # Todas as tasks
        await list_tasks(session)
        
        # Só tasks pendentes
        await list_tasks(session, status=TaskStatus.PENDING)
        
        # Limitar a 10
        await list_tasks(session, limit=10)
    """
    stmt = select(TaskRow).order_by(TaskRow.created_at.desc()).limit(limit)
    
    if status:
        stmt = stmt.where(TaskRow.status == status)
    
    result = await session.execute(stmt)
    return [r.to_task() for r in result.scalars().all()]


async def count_tasks(session: AsyncSession) -> dict:
    """
    Conta tasks por status.
    
    Retorna:
        {
            "total": 100,
            "pending": 10,
            "running": 5,
            "completed": 80,
            "failed": 5
        }
    """
    total = (await session.execute(
        select(func.count()).select_from(TaskRow)
    )).scalar_one()
    
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
    
    return {
        "total": total,
        "pending": pending,
        "running": running,
        "completed": completed,
        "failed": failed,
    }
