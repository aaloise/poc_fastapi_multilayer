# Async POC

POC com FastAPI + Queuefy + NiceGUI. Tudo async, arquitetura em camadas.

## 🚀 Comece Aqui

**Primeiro:** [GUIA_RAPIDO.md](GUIA_RAPIDO.md) - Como executar  
**Entenda:** [docs/ARQUITETURA_CORRETA.md](docs/ARQUITETURA_CORRETA.md) - Como funciona

## Resumo Rápido

```bash
cd backend

# 1. Instalar
uv sync

# 2. Popular banco
uv run python scripts/seed_data.py

# 3. Iniciar
uv run python -m app.main
```

**Acesse:**
- Dashboard: http://localhost:8000/ui/
- API: http://localhost:8000/api/v1/
- Docs: http://localhost:8000/docs

## 🧪 Testar

```bash
# Testes interativos
uv run python scripts/test_interactive.py

# Benchmark
uv run python scripts/benchmark.py
```

## 📁 Estrutura

```
backend/
├── src/app/
│   ├── main.py          # Entry point (API + UI + Queue)
│   ├── config.py        # Configurações
│   ├── models.py        # Domain + DB models
│   ├── services.py      # Business logic
│   ├── routes.py        # API endpoints
│   ├── ui.py            # NiceGUI dashboard
│   ├── queue.py         # Queuefy integration
│   ├── flows.py         # Prefect flows
│   └── database.py      # DB setup
│
├── scripts/
│   ├── seed_data.py     # Popula banco
│   ├── test_interactive.py  # Testes
│   └── benchmark.py     # Performance
│
└── docs/                # Documentação detalhada
```

## 📊 Stack

- **FastAPI** - API REST
- **NiceGUI** - Dashboard visual
- **Queuefy** - Task queue async
- **SQLAlchemy** - ORM async
- **SQLite** - Banco (dev)
- **PostgreSQL** - Banco (prod)
- **uvloop** - Event loop (Linux/Mac)
- **asyncio** - Event loop (Windows)

## 📖 Documentação

### Essencial
- [GUIA_RAPIDO.md](GUIA_RAPIDO.md) - **Comece aqui!**
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura
- [docs/QUEUEFY.md](docs/QUEUEFY.md) - Como Queuefy funciona

### Detalhada
- [docs/DATABASE.md](docs/DATABASE.md) - Modelo de banco
- [docs/FASTAPI.md](docs/FASTAPI.md) - FastAPI completo
- [docs/NICEGUI.md](docs/NICEGUI.md) - NiceGUI completo
- [docs/PREFECT.md](docs/PREFECT.md) - Prefect flows
- [docs/SERVICES.md](docs/SERVICES.md) - Business logic
- [docs/GRANIAN.md](docs/GRANIAN.md) - Servidor ASGI
- [docs/TESTING.md](docs/TESTING.md) - Testes unitários
- [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) - Guia de testes
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deploy

## 🐛 Problemas?

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
- Tudo funciona normalmente, só é um pouco mais lento
- Veja [docs/WINDOWS.md](docs/WINDOWS.md)
