# Async POC — FastAPI + uvloop + Granian + Prefect + Queuefy + NiceGUI

POC com arquitetura em camadas, 100% async.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │   FastAPI REST API   │  │     NiceGUI (UI Pages)       │ │
│  │   /api/v1/*          │  │     /ui/*                    │ │
│  └──────────┬───────────┘  └──────────────┬───────────────┘ │
├─────────────┼──────────────────────────────┼────────────────┤
│             │     APPLICATION LAYER        │                │
│  ┌──────────▼──────────────────────────────▼───────────────┐ │
│  │              TaskService (Use Cases)                     │ │
│  │   create_task() │ execute_task() │ list_tasks()         │ │
│  └──────────┬──────────────────────────────┬───────────────┘ │
├─────────────┼──────────────────────────────┼────────────────┤
│             │        DOMAIN LAYER          │                │
│  ┌──────────▼──────────┐  ┌───────────────▼──────────────┐  │
│  │  Entities & VOs     │  │   Repository Ports (Protocol)│  │
│  │  Task, TaskResult   │  │   TaskRepository             │  │
│  │  TaskStatus, ...    │  │                              │  │
│  └─────────────────────┘  └───────────────┬──────────────┘  │
├────────────────────────────────────────────┼────────────────┤
│              INFRASTRUCTURE LAYER          │                │
│  ┌──────────────┐ ┌──────────┐ ┌─────────▼──────────────┐  │
│  │ SQLAlchemy   │ │ Queuefy  │ │    Prefect Flows       │  │
│  │ (async DB)   │ │ (Queue)  │ │    (Orchestration)     │  │
│  └──────────────┘ └──────────┘ └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Server: Granian (Rust) + uvloop (async event loop)
```

## 🚀 Como Executar

### Instalação

```bash
cd backend
pip install -e ".[dev]"
```

### Desenvolvimento

```bash
# Com uvicorn (dev)
python -m app.main

# Com Granian (produção)
granian --interface asgi --config granian.toml app.main:app

# Ou diretamente
python -m app.main --granian
```

### Endpoints

- **API REST**: http://localhost:8000/api/v1/
- **NiceGUI Dashboard**: http://localhost:8000/ui/
- **Arquitetura**: http://localhost:8000/ui/architecture
- **Monitor**: http://localhost:8000/ui/monitor
- **Swagger Docs**: http://localhost:8000/docs

## 📦 Stack

| Tecnologia | Função |
|-----------|--------|
| **FastAPI** | Framework HTTP async |
| **uvloop** | Event loop ultra-rápido |
| **Granian** | Servidor ASGI em Rust |
| **Queuefy** | Fila de tarefas async (sem broker) |
| **Prefect** | Orquestração de workflows |
| **NiceGUI** | UI interativa (montada no FastAPI) |
| **SQLAlchemy 2** | ORM async |
| **aiosqlite** | Driver SQLite async |

## 📁 Estrutura

```
backend/
├── pyproject.toml          # Dependências
├── granian.toml            # Config do Granian
├── src/app/
│   ├── main.py             # Entry point + lifespan
│   ├── config.py           # Settings (pydantic-settings)
│   ├── dependencies.py     # DI wiring
│   ├── domain/             # Entidades & ports
│   ├── application/        # Use cases
│   ├── infrastructure/     # DB, Queuefy, Prefect
│   └── presentation/       # API routes + NiceGUI
```
