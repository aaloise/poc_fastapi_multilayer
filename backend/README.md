# Async POC

POC com FastAPI + Granian + Queuefy + NiceGUI + Joblib + Prefect. Tudo async, arquitetura flat.

## 🚀 Quick Start

```bash
cd backend

# 1. Instalar dependências
uv sync

# 2. Popular banco
uv run python scripts/seed_data.py

# 3. Iniciar aplicação
uv run python -m app.main
```

**Acesse:**
- Dashboard: http://localhost:8000/ui/
- API: http://localhost:8000/api/v1/
- Docs: http://localhost:8000/docs

## 📦 Stack

| Tecnologia | Função | Tipo |
|-----------|--------|------|
| **FastAPI** | API REST | I/O-bound (async) |
| **Granian** | Servidor ASGI (Rust) | Server |
| **uvloop** | Event loop rápido | Runtime |
| **NiceGUI** | Dashboard visual | UI |
| **Queuefy** | Task queue | I/O-bound (async) |
| **Joblib** | Processamento paralelo | CPU-bound (parallel) |
| **Prefect** | Orquestração de workflows | Orchestration |
| **SQLAlchemy** | ORM async | Database |

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│              main.py (único processo)                    │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │   NiceGUI    │    │   FastAPI    │                   │
│  │   (UI)       │    │   (API REST) │                   │
│  └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                            │
│         └────────┬──────────┘                            │
│                  │                                       │
│                  ↓                                       │
│         ┌────────────────┐                              │
│         │   services.py  │                              │
│         │  (Business)    │                              │
│         └────────┬───────┘                              │
│                  │                                       │
│         ┌────────┼────────┬──────────┐                 │
│         │        │        │          │                 │
│         ↓        ↓        ↓          ↓                 │
│  ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────────┐         │
│  │database  │ │queue │ │joblib│ │ prefect  │         │
│  │(SQLA)    │ │(Qfy) │ │(CPU) │ │ (flows)  │         │
│  └──────────┘ └──────┘ └──────┘ └──────────┘         │
└─────────────────────────────────────────────────────────┘
```

### Quando usar cada componente?

| Componente | Use para | Exemplo |
|-----------|----------|---------|
| **Queuefy** | I/O-bound, async | API calls, DB queries, file I/O |
| **Joblib** | CPU-bound, parallel | ML training, data processing, cálculos pesados |
| **Prefect** | Workflows complexos | ETL pipelines, orquestração multi-step |

## 📁 Estrutura

```
backend/
├── src/app/
│   ├── main.py          # Entry point (API + UI + Queue + Parallel)
│   ├── config.py        # Configurações multi-ambiente
│   ├── models.py        # Domain + DB models
│   ├── services.py      # Business logic
│   ├── routes.py        # API endpoints
│   ├── ui.py            # NiceGUI dashboard
│   ├── queue.py         # Queuefy (I/O-bound tasks)
│   ├── parallel.py      # Joblib (CPU-bound tasks)
│   ├── flows.py         # Prefect (workflows)
│   └── database.py      # DB setup
│
├── scripts/
│   ├── seed_data.py     # Popula banco
│   ├── test_interactive.py  # Testes
│   └── benchmark.py     # Performance
│
├── tests/               # Testes unitários
├── docs/                # Documentação detalhada
├── pyproject.toml       # Dependências (Python 3.14+)
└── README.md            # Este arquivo
```

## 🧪 Testar

```bash
# Testes interativos
uv run python scripts/test_interactive.py

# Benchmark
uv run python scripts/benchmark.py

# Testes unitários
uv run pytest tests/ -v
```

## 📊 Endpoints

### API REST
- `POST /api/v1/tasks` - Criar task
- `GET /api/v1/tasks` - Listar tasks
- `GET /api/v1/tasks/{id}` - Buscar task
- `GET /api/v1/tasks/stats` - Estatísticas
- `GET /api/v1/health` - Health check

### Processamento Paralelo
- `POST /api/v1/parallel/compute` - Computação paralela (Joblib)

### Workflows
- `POST /api/v1/flows/pipeline` - Pipeline ETL (Prefect)
- `POST /api/v1/flows/batch` - Batch process (Prefect)

## 🐍 Python 3.14+

Esta POC usa **Python 3.14** (lançado em outubro de 2025) ou superior.

**Novidades do Python 3.14:**
- Template string literals
- Deferred evaluation of annotations
- Suporte a free-threaded Python (no GIL)

**Python 3.15** (outubro de 2026):
- Lazy imports
- `frozendict` e `sentinel` builtins
- UTF-8 mode por padrão

## 📖 Documentação

- `docs/ARCHITECTURE.md` - Arquitetura
- `docs/QUEUEFY.md` - Queuefy (I/O-bound)
- `docs/JOBLIB.md` - Joblib (CPU-bound)
- `docs/PREFECT.md` - Prefect (workflows)
- `docs/DATABASE.md` - Modelo de banco
- `docs/FASTAPI.md` - FastAPI
- `docs/NICEGUI.md` - NiceGUI
- `docs/GRANIAN.md` - Granian
- `docs/TESTING.md` - Testes
- `docs/DEPLOYMENT.md` - Deploy

## 🐛 Troubleshooting

**ModuleNotFoundError:**
```bash
uv sync
```

**Porta em uso:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Windows:**
- uvloop não funciona (usa asyncio automaticamente)
- Tudo funciona normalmente
