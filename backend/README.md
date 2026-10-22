# Async POC — FastAPI + Granian + Queuefy + NiceGUI

POC 100% async com estrutura simples e direta.

## 📁 Estrutura (Flat & Simple)

```
backend/
├── pyproject.toml      # uv + dependências
├── granian.toml        # Config do servidor
├── Makefile            # Comandos úteis
├── Dockerfile          # Container
├── docker-compose.yml  # Stack completa
│
└── src/app/
    ├── main.py         # Entry point + lifespan
    ├── config.py       # Settings (pydantic)
    ├── models.py       # Domain + DB models (juntos)
    ├── services.py     # Business logic
    ├── routes.py       # FastAPI routes
    ├── ui.py           # NiceGUI pages
    ├── queue.py        # Queuefy integration
    ├── flows.py        # Prefect flows
    └── database.py     # DB setup
```

**Sem camadas desnecessárias.** Tudo flat, direto ao ponto.

## 🚀 Como Rodar

### Com uv (recomendado)

```bash
cd backend

# Instala dependências
uv sync

# Desenvolvimento
uv run python -m app.main

# Produção (Granian + uvloop)
uv run granian --interface asgi --config granian.toml app.main:app
```

### Com pip (fallback)

```bash
pip install -e .
python -m app.main
```

### Docker

```bash
docker-compose up -d
```

## 🌐 Endpoints

- **API**: http://localhost:8000/api/v1/
- **Dashboard**: http://localhost:8000/ui/
- **Docs**: http://localhost:8000/docs

## 📦 Stack

| Tecnologia | Função |
|-----------|--------|
| **FastAPI** | Framework HTTP async |
| **uvloop** | Event loop ultra-rápido |
| **Granian** | Servidor ASGI em Rust |
| **Queuefy** | Fila async (sem broker) |
| **Prefect** | Orquestração (opcional) |
| **NiceGUI** | UI interativa |
| **SQLAlchemy** | ORM async |

## 🔄 Fluxo Simples

```
HTTP Request
    ↓
Granian (Rust) + uvloop
    ↓
FastAPI Router
    ↓
Service (business logic)
    ↓
DB (SQLAlchemy async) / Queue (Queuefy)
    ↓
Worker (background)
    ↓
Response
```

## 🧪 Testes

```bash
uv run pytest tests/ -v
```

## 📝 Comandos (Makefile)

```bash
make install      # uv sync
make dev          # Rodar em dev
make granian      # Rodar com Granian
make test         # Testes
make lint         # Linting
make docker-up    # Docker
```
