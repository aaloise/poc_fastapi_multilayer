# ⚡ Referência Rápida de Comandos

## Instalação e Setup

```bash
# Instalar dependências
uv sync

# Popular banco com dados de exemplo
uv run python scripts/seed_data.py

# Verificar setup
uv run python scripts/verify_setup.py
```

## Execução

```bash
# Iniciar aplicação (API + Dashboard + Queue)
uv run python -m app.main

# Com ambiente específico
POC_ENV=production uv run python -m app.main
POC_ENV=testing uv run python -m app.main

# Com porta diferente
POC_PORT=8001 uv run python -m app.main

# Com log level diferente
POC_LOG_LEVEL=DEBUG uv run python -m app.main
```

## Testes

```bash
# Testes interativos
uv run python scripts/test_interactive.py

# Benchmark de performance
uv run python scripts/benchmark.py

# Benchmark intenso
uv run python scripts/benchmark.py --requests 100

# Testes unitários
uv run pytest tests/ -v
```

## API (curl)

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Listar tasks
curl http://localhost:8000/api/v1/tasks

# Listar com filtro
curl "http://localhost:8000/api/v1/tasks?status=pending&limit=10"

# Buscar task por ID
curl http://localhost:8000/api/v1/tasks/{task_id}

# Criar task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "test_task", "payload": {"foo": "bar"}, "priority": "medium"}'

# Estatísticas
curl http://localhost:8000/api/v1/tasks/stats

# Executar pipeline Prefect
curl -X POST "http://localhost:8000/api/v1/flows/pipeline?source=api"
```

## Banco de Dados

```bash
# SQLite (development)
sqlite3 dev_poc.db
.tables
SELECT * FROM tasks;
SELECT * FROM queuefy_runs;
.quit

# PostgreSQL (production)
docker exec -it poc-postgres psql -U poc -d poc_prod
\dt
SELECT * FROM tasks;
\q
```

## Docker

```bash
# Build imagem
docker build -t async-poc .

# Rodar container
docker run -p 8000:8000 async-poc

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f
```

## Produção

```bash
# Setup PostgreSQL
./scripts/setup_production.sh

# Iniciar com PostgreSQL
POC_ENV=production uv run python -m app.main

# Com Granian (mais rápido)
POC_ENV=production uv run granian --interface asgi app.main:app
```

## Desenvolvimento

```bash
# Script de desenvolvimento
uv run python scripts/dev.py start    # Iniciar
uv run python scripts/dev.py seed     # Popular banco
uv run python scripts/dev.py test     # Testar
uv run python scripts/dev.py reset    # Resetar banco
uv run python scripts/dev.py logs     # Ver logs
uv run python scripts/dev.py shell    # Shell Python
```

## Troubleshooting

```bash
# Verificar setup
uv run python scripts/verify_setup.py

# Matar processo na porta 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Resetar ambiente
# Windows PowerShell
Remove-Item -Recurse -Force .venv
uv sync

# Linux/Mac
rm -rf .venv
uv sync
```

## Makefile (se disponível)

```bash
make install          # Instalar dependências
make dev              # Iniciar em desenvolvimento
make prod             # Iniciar em produção
make test             # Executar testes
make seed             # Popular banco
make reset            # Resetar banco
make logs             # Ver logs
make shell            # Shell Python
make benchmark        # Benchmark
make docker-build     # Build Docker
make docker-up        # Docker Compose up
make docker-down      # Docker Compose down
```

## URLs

```
Dashboard:    http://localhost:8000/ui/
API:          http://localhost:8000/api/v1/
Docs:         http://localhost:8000/docs
Health:       http://localhost:8000/api/v1/health
Tasks:        http://localhost:8000/api/v1/tasks
Stats:        http://localhost:8000/api/v1/tasks/stats
```

## Variáveis de Ambiente

```bash
POC_ENV=development|production|testing
POC_HOST=127.0.0.1
POC_PORT=8000
POC_DB_URL=sqlite+aiosqlite:///./dev_poc.db
POC_DB_ECHO=false
POC_QUEUE_CONCURRENCY=4
POC_LOG_LEVEL=INFO
POC_DEBUG=true
```

## Estrutura de Arquivos

```
backend/
├── src/app/
│   ├── main.py          # Entry point
│   ├── config.py        # Configurações
│   ├── models.py        # Modelos
│   ├── services.py      # Lógica de negócio
│   ├── routes.py        # API endpoints
│   ├── ui.py            # Dashboard
│   ├── queue.py         # Fila
│   ├── flows.py         # Prefect flows
│   └── database.py      # Banco
│
├── scripts/
│   ├── seed_data.py     # Popular banco
│   ├── test_interactive.py  # Testes
│   ├── benchmark.py     # Performance
│   ├── dev.py           # Dev tools
│   └── verify_setup.py  # Verificar setup
│
├── tests/               # Testes unitários
├── docs/                # Documentação
├── pyproject.toml       # Dependências
└── README.md            # Este arquivo
```

## Documentação

```
GUIA_RAPIDO.md       # Comece aqui!
COMO_FUNCIONA.md     # Como tudo funciona
PROBLEMAS.md         # Troubleshooting
REFERENCIA.md        # Este arquivo

docs/
├── ARCHITECTURE.md  # Arquitetura
├── QUEUEFY.md       # Queuefy
├── DATABASE.md      # Banco de dados
├── FASTAPI.md       # FastAPI
├── NICEGUI.md       # NiceGUI
├── PREFECT.md       # Prefect
├── SERVICES.md      # Services
├── GRANIAN.md       # Granian
├── TESTING.md       # Testes
├── TESTING_GUIDE.md # Guia de testes
├── DEPLOYMENT.md    # Deploy
└── WINDOWS.md       # Windows
```

## Fluxo de Trabalho Típico

```bash
# 1. Setup inicial
uv sync
uv run python scripts/seed_data.py

# 2. Iniciar aplicação
uv run python -m app.main

# 3. Em outro terminal, testar
uv run python scripts/test_interactive.py

# 4. Acessar dashboard
# http://localhost:8000/ui/

# 5. Benchmark
uv run python scripts/benchmark.py

# 6. Parar aplicação (Ctrl+C)
```

## Comandos Úteis

```bash
# Ver versão do Python
uv run python --version

# Ver pacotes instalados
uv pip list

# Ver informações do pacote
uv pip show async-poc

# Atualizar dependências
uv sync --upgrade

# Limpar cache
uv cache clean

# Verificar dependências
uv pip check
```
