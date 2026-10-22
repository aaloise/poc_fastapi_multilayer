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
├── src/app/
│   ├── main.py         # Entry point + lifespan
│   ├── config.py       # Settings (pydantic)
│   ├── models.py       # 📦 Domain + DB models (tabela: tasks)
│   ├── services.py     # ⚙️ Business logic
│   ├── routes.py       # 🔌 FastAPI routes
│   ├── ui.py           # 🎨 NiceGUI pages
│   ├── queue.py        # 📊 Queuefy (tabelas: queuefy_*)
│   ├── flows.py        # 🔮 Prefect flows
│   └── database.py     # 🗄️ DB setup
│
└── docs/
    ├── QUEUEFY.md      # 📖 Como o Queuefy funciona
    └── DATABASE.md     # 📖 Modelo de banco de dados
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

## 📊 Como o Queuefy Funciona

```
1. API recebe request
   POST /api/v1/tasks
   ↓
2. Cria task no banco (tabela: tasks)
   status: pending
   ↓
3. Enfileira no Queuefy (tabela: queuefy_runs)
   status: pending
   ↓
4. Worker em background busca tasks pendentes
   ↓
5. Executa o handler registrado
   ↓
6. Atualiza status para completed/failed
```

**📖 [Leia mais em docs/QUEUEFY.md](docs/QUEUEFY.md)**

## 🗄️ Modelo de Banco de Dados

### Tabela `tasks` (sua aplicação)

```sql
CREATE TABLE tasks (
    id           VARCHAR(36) PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    payload      JSON,
    status       VARCHAR(20) DEFAULT 'pending',
    priority     VARCHAR(20) DEFAULT 'medium',
    queue        VARCHAR(100) DEFAULT 'default',
    attempts     INTEGER DEFAULT 0,
    created_at   DATETIME,
    started_at   DATETIME,
    completed_at DATETIME,
    error        VARCHAR(1000)
);
```

### Tabela `queuefy_runs` (Queuefy)

```sql
CREATE TABLE queuefy_runs (
    id           VARCHAR(36) PRIMARY KEY,
    task_name    VARCHAR(255) NOT NULL,
    task_id      VARCHAR(36),
    kwargs       JSON,
    status       VARCHAR(20),
    attempts     INTEGER,
    created_at   DATETIME,
    ...
);
```

**📖 [Leia mais em docs/DATABASE.md](docs/DATABASE.md)**

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

## 📚 Documentação

- [Como o Queuefy funciona](docs/QUEUEFY.md)
- [Modelo de banco de dados](docs/DATABASE.md)
- [Queuefy no GitHub](https://github.com/paulocoutinhox/queuefy)
