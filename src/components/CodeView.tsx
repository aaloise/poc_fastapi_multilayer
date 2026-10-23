import { useState } from 'react';

interface CodeFile {
  name: string;
  path: string;
  icon: string;
  description: string;
  code: string;
}

const codeFiles: CodeFile[] = [
  {
    name: 'main.py',
    path: 'src/app/main.py',
    icon: '🚀',
    description: 'Entry point — setup e lifespan',
    code: `"""Entry point — setup e lifespan."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

# uvloop — event loop rápido
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from app.config import get_settings
from app.database import init_db, close_db
from app.queue import init_queue, stop_queue
from app.routes import router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown."""
    # Startup
    await init_db(settings.db_url)
    await init_queue(_engine, settings.queue_concurrency)
    yield
    # Shutdown
    await stop_queue()
    await close_db()

app = FastAPI(title="Async POC", lifespan=lifespan)
app.include_router(router)`,
  },
  {
    name: 'config.py',
    path: 'src/app/config.py',
    icon: '⚙️',
    description: 'Settings centralizadas',
    code: `"""Configuração centralizada."""

from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Tudo em um lugar. Override via env vars (POC_*)."""
    
    app_name: str = "Async POC"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    db_url: str = "sqlite+aiosqlite:///./poc.db"
    queue_concurrency: int = 8
    ui_prefix: str = "/ui"

@lru_cache
def get_settings() -> Settings:
    return Settings()`,
  },
  {
    name: 'models.py',
    path: 'src/app/models.py',
    icon: '📦',
    description: 'Domain + DB models juntos',
    code: `"""Modelos — domain + DB em um arquivo só."""

import uuid
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Enums
class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Domain model
class Task(BaseModel):
    """Task — entidade principal."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    payload: dict = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

# DB model
class TaskRow(DeclarativeBase):
    """Linha no banco."""
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(index=True)
    # ... outros campos

# DB operations
async def save_task(session, task: Task) -> Task:
    """Salva task no banco."""
    ...

async def get_task(session, task_id) -> Task | None:
    """Busca task."""
    ...`,
  },
  {
    name: 'services.py',
    path: 'src/app/services.py',
    icon: '⚙️',
    description: 'Business logic',
    code: `"""Serviços — lógica de negócio."""

import uuid
from datetime import datetime
from app.database import get_session
from app.models import Task, TaskStatus, save_task, get_task

async def create_task(name: str, payload: dict | None = None) -> Task:
    """Cria uma nova task."""
    task = Task(name=name, payload=payload or {})
    
    session = await get_session()
    async with session:
        task = await save_task(session, task)
    
    return task

async def execute_task(task_id: uuid.UUID) -> dict:
    """Executa uma task (chamado pelo worker)."""
    session = await get_session()
    async with session:
        task = await get_task(session, task_id)
        if not task:
            return {"success": False, "error": "Not found"}
        
        # Mark running
        task.status = TaskStatus.RUNNING
        await save_task(session, task)
        
        # Process (async work)
        import asyncio
        await asyncio.sleep(0.1)
        
        # Mark completed
        task.status = TaskStatus.COMPLETED
        await save_task(session, task)
    
    return {"success": True, "task_id": str(task_id)}

async def get_all_tasks(limit: int = 50) -> list[Task]:
    """Lista tasks."""
    session = await get_session()
    async with session:
        return await list_tasks(session, limit=limit)`,
  },
  {
    name: 'routes.py',
    path: 'src/app/routes.py',
    icon: '🔌',
    description: 'FastAPI endpoints',
    code: `"""FastAPI Routes — endpoints HTTP."""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models import Task, TaskStatus, Priority
from app.services import create_task, get_task_by_id, get_all_tasks, get_stats

router = APIRouter(prefix="/api/v1")

class CreateTaskRequest(BaseModel):
    name: str
    payload: dict = {}
    priority: Priority = Priority.MEDIUM

@router.post("/tasks", status_code=201)
async def create_task_endpoint(req: CreateTaskRequest):
    """Cria task."""
    task = await create_task(name=req.name, payload=req.payload)
    return {"id": str(task.id), "name": task.name, "status": task.status}

@router.get("/tasks")
async def list_tasks_endpoint(limit: int = 50):
    """Lista tasks."""
    tasks = await get_all_tasks(limit=limit)
    return [{"id": str(t.id), "name": t.name} for t in tasks]

@router.get("/tasks/{task_id}")
async def get_task_endpoint(task_id: uuid.UUID):
    """Busca task."""
    task = await get_task_by_id(task_id)
    if not task:
        raise HTTPException(404, "Not found")
    return {"id": str(task.id), "name": task.name, "status": task.status}

@router.get("/tasks/stats")
async def get_stats_endpoint():
    """Estatísticas."""
    return await get_stats()

@router.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "version": "0.1.0"}`,
  },
  {
    name: 'queue.py',
    path: 'src/app/queue.py',
    icon: '📊',
    description: 'Queuefy — task queue',
    code: `"""Queuefy — fila de tarefas async."""

import uuid
from queuefy.app import Queuefy
from queuefy.store.sqlalchemy import SqlAlchemyStore
from queuefy.worker import Worker

_queuefy: Queuefy | None = None

async def init_queue(engine, concurrency: int = 8):
    """Inicializa Queuefy."""
    global _queuefy
    _queuefy = Queuefy(SqlAlchemyStore(engine))
    await _queuefy.setup()
    
    # Registra handlers
    @_queuefy.task("process_task", max_attempts=3)
    async def handle_task(task_id: str, payload: dict):
        from app.services import execute_task
        return await execute_task(uuid.UUID(task_id))
    
    # Inicia worker em background
    import asyncio
    worker = Worker(_queuefy, concurrency=concurrency)
    asyncio.create_task(worker.run())

async def enqueue(task_name: str, **kwargs) -> str:
    """Enfileira uma task."""
    tid = kwargs.get("task_id") or str(uuid.uuid4())
    await _queuefy.enqueue(task_name, task_id=tid, **kwargs)
    return tid`,
  },
  {
    name: 'flows.py',
    path: 'src/app/flows.py',
    icon: '🔮',
    description: 'Prefect flows (opcional)',
    code: `"""Prefect Flows — orquestração (opcional)."""

import asyncio
from datetime import datetime

try:
    from prefect import flow, task, get_run_logger
    PREFECT_OK = True
except ImportError:
    PREFECT_OK = False

if PREFECT_OK:
    @task(retries=3)
    async def fetch_data(source: str) -> dict:
        """Busca dados."""
        await asyncio.sleep(0.5)
        return {"source": source, "records": 100}
    
    @task
    async def transform(data: dict) -> dict:
        """Transforma dados."""
        await asyncio.sleep(0.2)
        return {"transformed": True, "count": data["records"]}
    
    @flow(name="data-pipeline")
    async def data_pipeline(source: str = "api") -> dict:
        """Pipeline ETL completo."""
        log = get_run_logger()
        log.info(f"Pipeline: {source}")
        
        raw = await fetch_data(source)
        result = await transform(raw)
        
        return result

else:
    async def data_pipeline(source: str = "api") -> dict:
        return {"error": "Prefect not installed"}`,
  },
  {
    name: 'database.py',
    path: 'src/app/database.py',
    icon: '🗄️',
    description: 'DB setup',
    code: `"""Database — setup e session."""

from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)
from app.models import Base

_engine = None
_session_factory = None

async def init_db(url: str):
    """Inicializa o banco."""
    global _engine, _session_factory
    
    _engine = create_async_engine(url)
    _session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Retorna session."""
    return _session_factory()

async def close_db():
    """Fecha engine."""
    global _engine
    if _engine:
        await _engine.dispose()`,
  },
  {
    name: 'ui.py',
    path: 'src/app/ui.py',
    icon: '🎨',
    description: 'NiceGUI pages',
    code: `"""NiceGUI — Dashboard interativo."""

from nicegui import ui

def setup_ui(prefix: str = "/ui"):
    """Registra páginas."""
    
    @ui.page(f"{prefix}/")
    async def dashboard():
        ui.dark_mode().enable()
        
        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("⚡ Async POC").classes("text-xl")
        
        # Stats
        with ui.row().classes("w-full gap-4 p-4"):
            with ui.card().classes("flex-1"):
                ui.label("📊 Tasks")
                stats = ui.label("Loading...")
        
        # Create task
        with ui.card().classes("w-full p-4"):
            ui.label("🚀 Create Task")
            name = ui.input("Name", value="demo")
            ui.button("Create", on_click=create_action)
        
        # Task list
        table = ui.table(columns=[...], rows=[])
        
        async def refresh():
            # Fetch from API
            ...`,
  },
  {
    name: 'pyproject.toml',
    path: 'pyproject.toml',
    icon: '📋',
    description: 'uv + dependências',
    code: `[project]
name = "async-poc"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "uvloop>=0.20.0",
    "granian[uvloop]>=1.6.0",
    "nicegui>=2.0",
    "queuefy[sqlalchemy]>=1.0.3",
    "sqlalchemy[asyncio]>=2.0",
    "aiosqlite>=0.20.0",
    "prefect>=3.0",
    "httpx>=0.27",
    "structlog>=24.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.6",
]`,
  },
];

export default function CodeView() {
  const [selectedFile, setSelectedFile] = useState(0);
  const file = codeFiles[selectedFile];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">Código-Fonte</h2>
        <p className="text-slate-400">9 arquivos — simples e direto</p>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* File list */}
        <div className="lg:col-span-1">
          <div className="glass-card p-4 sticky top-32">
            <h3 className="font-bold text-sm text-slate-400 mb-3 uppercase tracking-wider">Arquivos</h3>
            <div className="space-y-1">
              {codeFiles.map((f, idx) => (
                <button
                  key={f.path}
                  onClick={() => setSelectedFile(idx)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                    idx === selectedFile
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-base">{f.icon}</span>
                    <span className="truncate">{f.name}</span>
                  </div>
                  <span className="text-xs text-slate-500 ml-6">{f.description}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Code display */}
        <div className="lg:col-span-3">
          <div className="glass-card overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50 bg-slate-800/50">
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <span className="text-sm text-slate-400 font-mono">{file.path}</span>
              </div>
              <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">{file.icon} {file.name}</span>
            </div>

            <pre className="p-4 overflow-x-auto text-sm leading-relaxed">
              <code className="text-slate-300">
                {file.code.split('\n').map((line, idx) => (
                  <div key={idx} className="flex">
                    <span className="text-slate-600 select-none w-8 text-right mr-4 shrink-0">{idx + 1}</span>
                    <span className="whitespace-pre">{line}</span>
                  </div>
                ))}
              </code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
