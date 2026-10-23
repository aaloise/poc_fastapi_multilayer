# Async POC — FastAPI + Granian + Queuefy + NiceGUI

POC 100% async com estrutura simples e direta, usando **uv** para gerenciamento de dependências.

## 📁 Estrutura

```
backend/
├── pyproject.toml      # uv + dependências
├── granian.toml        # Config do servidor
├── Makefile            # Comandos úteis
├── Dockerfile          # Container
├── docker-compose.yml  # Stack completa
│
├── src/app/
│   ├── main.py         # 🚀 Entry point + lifespan
│   ├── config.py       # ⚙️ Settings (pydantic)
│   ├── models.py       # 📦 Domain + DB models (tabela: tasks)
│   ├── services.py     # ⚙️ Business logic
│   ├── routes.py       # 🔌 FastAPI routes
│   ├── ui.py           # 🎨 NiceGUI pages
│   ├── queue.py        # 📊 Queuefy (tabelas: queuefy_*)
│   ├── flows.py        # 🔮 Prefect flows
│   └── database.py     # 🗄️ DB setup
│
└── docs/               # 📚 Documentação completa
    ├── ARCHITECTURE.md # Arquitetura e design
    ├── GRANIAN.md      # Servidor ASGI
    ├── FASTAPI.md      # Framework HTTP
    ├── NICEGUI.md      # Interface web
    ├── PREFECT.md      # Orquestração
    ├── SERVICES.md     # Lógica de negócio
    ├── DATABASE.md     # Modelo de banco
    ├── QUEUEFY.md      # Fila de tarefas
    ├── DEPLOYMENT.md   # Guia de deploy
    └── TESTING.md      # Guia de testes
```

## 🚀 Quick Start

### ⚠️ Importante: Configuração Inicial

Se você está executando pela primeira vez ou encontrou erros de `ModuleNotFoundError`, execute:

```bash
cd backend

# Remove ambiente virtual antigo (se existir)
rm -rf .venv  # Linux/macOS
# ou no Windows PowerShell:
Remove-Item -Recurse -Force .venv

# Reinstala dependências
uv sync

# Verifica se tudo está configurado corretamente
uv run python scripts/verify_setup.py
```

### Opção 1: Script de Desenvolvimento (Recomendado)

```bash
cd backend

# Instala dependências (se ainda não instalou)
uv sync

# Popula banco com dados de exemplo
uv run python scripts/dev.py seed

# Inicia API
uv run python scripts/dev.py start

# Em outro terminal, execute testes
uv run python scripts/dev.py test
```

### Opção 2: Makefile

```bash
cd backend

# Instala dependências
make install

# Popula banco
make seed

# Inicia API (dev)
make dev

# Em outro terminal
make test-interactive  # Testes interativos
make benchmark         # Benchmark de performance
```

### Opção 3: Manual

```bash
cd backend

# Instala dependências
uv sync

# Desenvolvimento (SQLite)
uv run python -m app.main

# Produção (PostgreSQL)
POC_ENV=production uv run python -m app.main

# Granian (recomendado para produção)
uv run granian --interface asgi --config granian.toml app.main:app
```

### Opção 4: Docker

```bash
docker-compose up -d
```

## 🌐 Endpoints

- **API**: http://localhost:8000/api/v1/
- **Dashboard**: http://localhost:8000/ui/
- **Docs**: http://localhost:8000/docs

## 📚 Documentação

### Core

- [🏗️ ARCHITECTURE.md](docs/ARCHITECTURE.md) — Arquitetura flat e design
- [⚙️ SERVICES.md](docs/SERVICES.md) — Lógica de negócio
- [📦 DATABASE.md](docs/DATABASE.md) — Modelo de banco de dados
- [📊 QUEUEFY.md](docs/QUEUEFY.md) — Fila de tarefas async

### Tecnologias

- [🦀 GRANIAN.md](docs/GRANIAN.md) — Servidor ASGI em Rust
- [⚡ FASTAPI.md](docs/FASTAPI.md) — Framework HTTP async
- [🎨 NICEGUI.md](docs/NICEGUI.md) — Interface web interativa
- [🔮 PREFECT.md](docs/PREFECT.md) — Orquestração de workflows

### Operações

- [🚀 DEPLOYMENT.md](docs/DEPLOYMENT.md) — Guia de deploy
- [🧪 TESTING.md](docs/TESTING.md) — Guia de testes

## 📊 Como Funciona

### Fluxo de Execução

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

### Tabelas no Banco

- **`tasks`** — Suas tasks de negócio
- **`queuefy_runs`** — Execuções do Queuefy (auto-criada)
- **`queuefy_schedules`** — Cron jobs (auto-criada)

## 📦 Stack

| Tecnologia | Função | Documentação |
|-----------|--------|--------------|
| **FastAPI** | Framework HTTP async | [FASTAPI.md](docs/FASTAPI.md) |
| **uvloop** | Event loop ultra-rápido | [GRANIAN.md](docs/GRANIAN.md) |
| **Granian** | Servidor ASGI em Rust | [GRANIAN.md](docs/GRANIAN.md) |
| **Queuefy** | Fila async (sem broker) | [QUEUEFY.md](docs/QUEUEFY.md) |
| **Prefect** | Orquestração (opcional) | [PREFECT.md](docs/PREFECT.md) |
| **NiceGUI** | UI interativa | [NICEGUI.md](docs/NICEGUI.md) |
| **SQLAlchemy** | ORM async | [DATABASE.md](docs/DATABASE.md) |

## 🔄 Arquitetura

```
┌─────────────────────────────────────────┐
│         Granian (Rust) + uvloop         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         FastAPI (routes.py)             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Services (services.py)             │
│      Business Logic                     │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  Database    │  │   Queuefy    │
│  (models.py) │  │  (queue.py)  │
└──────────────┘  └──────────────┘
```

**📖 [Leia mais em ARCHITECTURE.md](docs/ARCHITECTURE.md)**

## 🧪 Testes

```bash
# Todos os testes
uv run pytest tests/ -v

# Com coverage
uv run pytest --cov=src/app --cov-report=term-missing
```

**📖 [Leia mais em TESTING.md](docs/TESTING.md)**

## 📝 Comandos (Makefile)

```bash
make install      # uv sync
make dev          # Rodar em dev
make granian      # Rodar com Granian
make test         # Testes
make lint         # Linting
make docker-up    # Docker
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# .env
POC_APP_NAME=Async POC
POC_DEBUG=false
POC_HOST=0.0.0.0
POC_PORT=8000
POC_DB_URL=sqlite+aiosqlite:///./poc.db
POC_QUEUE_CONCURRENCY=8
POC_UI_PREFIX=/ui
```

Copie `.env.example` para `.env` e customize.

## 🚀 Deploy

### Docker

```bash
docker build -t async-poc .
docker run -p 8000:8000 async-poc
```

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

**📖 [Leia mais em DEPLOYMENT.md](docs/DEPLOYMENT.md)**

## 💡 Exemplos de Uso

### Criar Task

```python
# Via API
POST /api/v1/tasks
{
    "name": "send_email",
    "payload": {"to": "user@example.com"},
    "priority": "high"
}

# Via código
from app.services import create_task

task = await create_task(
    name="send_email",
    payload={"to": "user@example.com"},
    priority=Priority.HIGH
)
```

### Task Agendada

```python
from datetime import datetime, timedelta
from app.queue import enqueue_at

# Rodar daqui a 1 hora
await enqueue_at(
    "send_notification",
    when=datetime.utcnow() + timedelta(hours=1),
    message="Hello!",
    channel="email"
)
```

### Cron Job

```python
# queue.py
@_queuefy.task("daily_report", cron="0 4 * * *")
async def handle_daily_report():
    """Roda todo dia às 4h da manhã."""
    stats = await get_stats()
    return {"report": stats}
```

## 📖 Links Úteis

### Documentação Interna

- [Arquitetura](docs/ARCHITECTURE.md)
- [Serviços](docs/SERVICES.md)
- [Banco de Dados](docs/DATABASE.md)
- [Queuefy](docs/QUEUEFY.md)
- [Granian](docs/GRANIAN.md)
- [FastAPI](docs/FASTAPI.md)
- [NiceGUI](docs/NICEGUI.md)
- [Prefect](docs/PREFECT.md)
- [Deploy](docs/DEPLOYMENT.md)
- [Testes](docs/TESTING.md)

### Documentação Externa

- [Queuefy no GitHub](https://github.com/paulocoutinhox/queuefy)
- [Granian no GitHub](https://github.com/emmett-framework/granian)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [NiceGUI Docs](https://nicegui.io/documentation)
- [Prefect Docs](https://docs.prefect.io/)
- [uv Docs](https://docs.astral.sh/uv/)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 📞 Suporte

Para dúvidas e sugestões:
- Abra uma issue no GitHub
- Consulte a documentação em `docs/`
- Veja os exemplos de código em `src/app/`

---

**Desenvolvido com ❤️ usando FastAPI + Granian + Queuefy + NiceGUI**
