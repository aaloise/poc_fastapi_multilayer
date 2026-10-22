import { useState } from 'react';

interface CodeFile {
  name: string;
  path: string;
  language: string;
  layer: string;
  code: string;
}

const codeFiles: CodeFile[] = [
  {
    name: 'main.py',
    path: 'src/app/main.py',
    language: 'python',
    layer: 'Entry Point',
    code: `"""Main Application Entry Point — 100% Async"""

from contextlib import asynccontextmanager
import asyncio

import structlog
from fastapi import FastAPI

# uvloop — ultra-fast event loop
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from app.config import get_settings
from app.infrastructure import init_database, close_database, QueueManager
from app.application import TaskService
from app.presentation.api import router as api_router

settings = get_settings()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async lifespan — startup & shutdown."""
    # Startup
    engine = await init_database(settings.database_url)
    queue = QueueManager(engine, concurrency=settings.queue_concurrency)
    await queue.setup()
    await queue.start_worker()
    
    yield  # App is running
    
    # Shutdown
    await queue.stop_worker()
    await close_database()

app = FastAPI(title="Async POC", lifespan=lifespan)
app.include_router(api_router)

# Run with Granian:
# granian --interface asgi app.main:app`,
  },
  {
    name: 'domain/__init__.py',
    path: 'src/app/domain/__init__.py',
    language: 'python',
    layer: 'Domain',
    code: `"""Domain Layer — ZERO infrastructure dependencies."""

from enum import StrEnum
from typing import Protocol
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

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

class Task(BaseModel):
    """Core domain entity."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    payload: dict = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    queue_name: str = "default"
    max_attempts: int = 3
    attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def mark_running(self) -> None:
        self.status = TaskStatus.RUNNING
        self.attempts += 1
    
    def mark_completed(self) -> None:
        self.status = TaskStatus.COMPLETED

class TaskRepository(Protocol):
    """Port — infrastructure provides the adapter."""
    async def save(self, task: Task) -> Task: ...
    async def get_by_id(self, task_id: uuid.UUID) -> Task | None: ...
    async def list_all(self, limit: int = 50) -> list[Task]: ...
    async def count(self) -> int: ...`,
  },
  {
    name: 'application/__init__.py',
    path: 'src/app/application/__init__.py',
    language: 'python',
    layer: 'Application',
    code: `"""Application Layer — Use Cases / Orchestrators."""

import time
import uuid
import structlog
from app.domain import Task, TaskRepository, TaskStatus

logger = structlog.get_logger()

class TaskService:
    """Orchestrates task creation & execution."""
    
    def __init__(self, repository: TaskRepository, queue):
        self._repo = repository
        self._queue = queue
    
    async def create_task(
        self, name: str, payload: dict | None = None
    ) -> Task:
        """Create + enqueue a task."""
        task = Task(name=name, payload=payload or {})
        task = await self._repo.save(task)
        
        # Enqueue via Queuefy (async, no blocking)
        await self._queue.enqueue(
            task_name=name,
            task_id=str(task.id),
            payload=task.payload,
        )
        
        await logger.ainfo("task.created", task_id=str(task.id))
        return task
    
    async def execute_task(self, task_id: uuid.UUID):
        """Execute a task — called by Queuefy worker."""
        task = await self._repo.get_by_id(task_id)
        if not task:
            return None
        
        task.mark_running()
        await self._repo.save(task)
        
        # Async processing
        result = await self._process(task)
        task.mark_completed()
        await self._repo.save(task)
        
        return result
    
    async def _process(self, task: Task) -> dict:
        import asyncio
        await asyncio.sleep(0.1)  # Simulate I/O
        return {"processed": True, "name": task.name}`,
  },
  {
    name: 'infrastructure/queue.py',
    path: 'src/app/infrastructure/queue.py',
    language: 'python',
    layer: 'Infrastructure',
    code: `"""Infrastructure — Queuefy Integration (async task queue)."""

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine
from queuefy.app import Queuefy
from queuefy.store.sqlalchemy import SqlAlchemyStore
from queuefy.worker import Worker

logger = structlog.get_logger()

class QueueManager:
    """Wraps Queuefy for clean async interface."""
    
    def __init__(self, engine: AsyncEngine, concurrency: int = 8):
        self._store = SqlAlchemyStore(engine)
        self._app = Queuefy(self._store)
        self._worker: Worker | None = None
        self._concurrency = concurrency
    
    async def setup(self) -> None:
        """Initialize Queuefy tables."""
        await self._app.setup()
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        @self._app.task("process_task", max_attempts=3, timeout=60)
        async def handle_task(task_id: str, payload: dict):
            from app.dependencies import get_task_service
            service = await get_task_service()
            return await service.execute_task(uuid.UUID(task_id))
        
        @self._app.task("nightly_report", cron="0 4 * * *")
        async def handle_report():
            # Scheduled task — runs at 4 AM daily
            ...
    
    async def enqueue(self, task_name: str, **kwargs) -> str:
        """Enqueue a task for async execution."""
        await self._app.enqueue(task_name, **kwargs)
        return kwargs.get("task_id", "")
    
    async def start_worker(self) -> None:
        """Start background worker."""
        import asyncio
        self._worker = Worker(self._app, concurrency=self._concurrency)
        asyncio.create_task(self._worker.run())`,
  },
  {
    name: 'infrastructure/prefect_flows.py',
    path: 'src/app/infrastructure/prefect_flows.py',
    language: 'python',
    layer: 'Infrastructure',
    code: `"""Infrastructure — Prefect Flows (optional orchestration)."""

import asyncio
from datetime import datetime

try:
    from prefect import flow, task as prefect_task, get_run_logger
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

if PREFECT_AVAILABLE:
    
    @prefect_task(retries=3, retry_delay_seconds=10)
    async def fetch_external_data(source: str) -> dict:
        """Fetch data from external source."""
        log = get_run_logger()
        log.info(f"Fetching from {source}")
        await asyncio.sleep(0.5)
        return {"source": source, "records": 100}
    
    @prefect_task(retries=2)
    async def transform_data(raw: dict) -> dict:
        """Transform raw data."""
        await asyncio.sleep(0.2)
        return {"transformed": True, "count": raw["records"]}
    
    @flow(name="data-pipeline")
    async def data_pipeline_flow(source: str = "api") -> dict:
        """Complete ETL pipeline."""
        log = get_run_logger()
        log.info(f"Starting pipeline: {source}")
        
        raw = await fetch_external_data(source)
        transformed = await transform_data(raw)
        
        return {"status": "complete", "data": transformed}`,
  },
  {
    name: 'presentation/ui.py',
    path: 'src/app/presentation/ui.py',
    language: 'python',
    layer: 'Presentation',
    code: `"""Presentation — NiceGUI Pages (mounted on FastAPI)."""

from nicegui import ui
from datetime import datetime

def setup_nicegui_pages(prefix: str = "/ui") -> None:
    
    @ui.page(f"{prefix}/")
    async def dashboard():
        ui.dark_mode().enable()
        
        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("⚡ Async POC Dashboard").classes("text-xl")
        
        # Stats cards
        with ui.row().classes("w-full gap-4 p-4"):
            with ui.card().classes("flex-1"):
                ui.label("📊 Tasks").classes("text-lg font-bold")
                stats = ui.label("Loading...")
            
            with ui.card().classes("flex-1"):
                ui.label("⚡ Queue").classes("text-lg font-bold")
                queue = ui.label("Active")
        
        # Task creation
        with ui.card().classes("w-full p-4"):
            ui.label("🚀 Create Task").classes("text-lg")
            name = ui.input("Name", value="demo")
            ui.button("Create", on_click=create_action)
        
        # Auto-refresh
        ui.timer(5.0, lambda: refresh(stats))
    
    @ui.page(f"{prefix}/architecture")
    async def architecture():
        ui.label("🏗️ Architecture Overview")
        # ... layer visualization`,
  },
  {
    name: 'config.py',
    path: 'src/app/config.py',
    language: 'python',
    layer: 'Configuration',
    code: `"""Application settings — pydantic-settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POC_",
    )
    
    # App
    app_name: str = "Async POC"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database (async)
    database_url: str = "sqlite+aiosqlite:///./poc.db"
    
    # Queuefy
    queue_concurrency: int = 8
    
    # Prefect
    prefect_enabled: bool = True
    
    # NiceGUI
    nicegui_prefix: str = "/ui"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()`,
  },
  {
    name: 'granian.toml',
    path: 'granian.toml',
    language: 'toml',
    layer: 'Server Config',
    code: `# Granian ASGI Server (Rust-based)
# Docs: github.com/emmett-framework/granian

address = "0.0.0.0"
port = 8000
interface = "asgi"
http = "auto"
workers = 4
threads = 2
backpressure = 1024
enable-websocket = true
log-level = "info"
graceful-timeout = 30
respawn-failed-workers = true

# uvloop is auto-detected if installed
# pip install "granian[uvloop]"`,
  },
];

export default function CodeView() {
  const [selectedFile, setSelectedFile] = useState(0);

  const file = codeFiles[selectedFile];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">Código-Fonte</h2>
        <p className="text-slate-400">Estrutura completa da POC com separação em camadas</p>
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
                    <span className="text-base">
                      {f.layer === 'Domain' && '🧱'}
                      {f.layer === 'Application' && '⚙️'}
                      {f.layer === 'Infrastructure' && '🔧'}
                      {f.layer === 'Presentation' && '📡'}
                      {f.layer === 'Entry Point' && '🚀'}
                      {f.layer === 'Configuration' && '⚙️'}
                      {f.layer === 'Server Config' && '🦀'}
                    </span>
                    <span className="truncate">{f.name}</span>
                  </div>
                  <span className="text-xs text-slate-500 ml-6">{f.layer}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Code display */}
        <div className="lg:col-span-3">
          <div className="glass-card overflow-hidden">
            {/* File header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50 bg-slate-800/50">
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <span className="text-sm text-slate-400 font-mono">{file.path}</span>
              </div>
              <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">{file.language}</span>
            </div>

            {/* Code content */}
            <pre className="p-4 overflow-x-auto text-sm leading-relaxed">
              <code className="text-slate-300">
                {file.code.split('\n').map((line, idx) => (
                  <div key={idx} className="flex">
                    <span className="text-slate-600 select-none w-8 text-right mr-4 shrink-0">{idx + 1}</span>
                    <span className="whitespace-pre">{highlightPython(line)}</span>
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

// Simple syntax highlighting
function highlightPython(line: string): JSX.Element {
  // Keywords
  const keywords = /\b(async|await|def|class|from|import|return|if|else|try|except|with|as|None|True|False|self|raise|yield)\b/g;
  const strings = /(["'])(?:(?=(\\?))\2.)*?\1/g;
  const comments = /#.*/g;
  const decorators = /@\w+/g;
  const functions = /\b(\w+)\s*\(/g;

  // Simple approach: just return the line as-is with basic coloring
  // For a real app, use a proper syntax highlighter
  const parts: JSX.Element[] = [];
  let remaining = line;
  let key = 0;

  // Comment
  if (remaining.trimStart().startsWith('#') || remaining.trimStart().startsWith('"""')) {
    return <span key={key} className="text-slate-500 italic">{line}</span>;
  }

  // Decorator
  if (remaining.trimStart().startsWith('@')) {
    return <span key={key} className="text-purple-400">{line}</span>;
  }

  // Basic keyword highlighting
  const segments = remaining.split(/(\b(?:async|await|def|class|from|import|return|if|else|try|except|with|as|None|True|False|self|raise|yield|for|in|not|and|or|is)\b)/g);
  
  return (
    <span>
      {segments.map((seg, i) => {
        if (/^(async|await|def|class|from|import|return|if|else|try|except|with|as|None|True|False|self|raise|yield|for|in|not|and|or|is)$/.test(seg)) {
          return <span key={i} className="text-blue-400">{seg}</span>;
        }
        if (/^["']/.test(seg)) {
          return <span key={i} className="text-green-400">{seg}</span>;
        }
        return <span key={i}>{seg}</span>;
      })}
    </span>
  );
}
