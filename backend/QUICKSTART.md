# 🚀 Guia Rápido de Início

Este guia mostra como testar **todas** as funcionalidades da POC em poucos minutos.

## ⚡ Quick Start (3 passos)

### 1. Instalação

```bash
cd backend
uv sync
```

### 2. Popula banco com dados de exemplo

```bash
uv run python scripts/seed_data.py
```

### 3. Inicia a API

```bash
uv run python -m app.main
```

**Pronto!** Acesse:
- 📊 Dashboard: http://localhost:8000/ui/
- 🧪 Testes: http://localhost:8000/ui/tests
- 📚 Docs: http://localhost:8000/docs

---

## 🎯 Testando Tudo

### Opção 1: Testes Interativos (Automático)

```bash
uv run python scripts/test_interactive.py
```

**O que faz:**
- ✅ Testa 10 funcionalidades diferentes
- ✅ Mostra resultados em tempo real
- ✅ Exibe tabela com resumo final
- ✅ Tempo total: ~5 segundos

### Opção 2: Dashboard de Testes (Visual)

1. Acesse: http://localhost:8000/ui/tests
2. Clique em **"Executar Todos os Testes"**
3. Veja cada teste sendo executado
4. Confira logs e resultados

### Opção 3: Testes Manuais (curl)

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Criar task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "payload": {"foo": "bar"}}'

# Listar tasks
curl http://localhost:8000/api/v1/tasks

# Estatísticas
curl http://localhost:8000/api/v1/tasks/stats
```

---

## 📊 Ambientes

### Desenvolvimento (SQLite)

```bash
# Já está configurado por padrão
uv run python -m app.main
```

**Características:**
- Database: `dev_poc.db` (SQLite local)
- Debug: ✅ Habilitado
- Workers: 4
- Log Level: DEBUG

### Produção (PostgreSQL)

```bash
# Configura PostgreSQL via Docker
./scripts/setup_production.sh

# Inicia API
POC_ENV=production uv run python -m app.main
```

**Características:**
- Database: PostgreSQL (Docker)
- Debug: ❌ Desabilitado
- Workers: 8
- Log Level: WARNING

---

## 🧪 O que Testar

### 1. FastAPI Routes

```bash
# Criar task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "send_email", "payload": {"to": "user@example.com"}}'

# Listar tasks
curl http://localhost:8000/api/v1/tasks

# Buscar task por ID
curl http://localhost:8000/api/v1/tasks/{task_id}

# Estatísticas
curl http://localhost:8000/api/v1/tasks/stats
```

### 2. Queuefy (Task Queue)

```bash
# Cria task (será processada automaticamente pelo worker)
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "process_task", "payload": {}}'

# Aguarda 2 segundos
sleep 2

# Verifica status (deve estar "completed")
curl http://localhost:8000/api/v1/tasks/{task_id}
```

**No console da API, você verá:**
```
INFO:queuefy.enqueued task_name=process_task task_id=abc-123
INFO:queuefy.handler.process_task task_id=abc-123
INFO:task.completed task_id=abc-123
```

### 3. Prefect Flows

```bash
# Executa pipeline ETL
curl -X POST "http://localhost:8000/api/v1/flows/pipeline?source=test"
```

**No console:**
```
INFO:prefect.flow.data_pipeline Pipeline starting: test
INFO:prefect.task.fetch_data Fetching from test
INFO:prefect.flow.data_pipeline Pipeline done
```

### 4. NiceGUI Dashboard

Acesse: http://localhost:8000/ui/

**O que ver:**
- ✅ Stats cards (Total, Pending, Completed)
- ✅ Formulário para criar task
- ✅ Tabela com tasks recentes
- ✅ Botão de refresh

### 5. Database

#### SQLite (Dev)

```bash
sqlite3 dev_poc.db

# Lista tabelas
.tables

# Mostra tasks
SELECT * FROM tasks LIMIT 5;

# Sai
.quit
```

#### PostgreSQL (Prod)

```bash
docker exec -it poc-postgres psql -U poc -d poc_prod

# Lista tabelas
\dt

# Mostra tasks
SELECT id, name, status FROM tasks LIMIT 5;

# Sai
\q
```

---

## ⚡ Benchmark

```bash
# Benchmark básico (10 requests)
uv run python scripts/benchmark.py

# Benchmark intenso (100 requests)
uv run python scripts/benchmark.py --requests 100
```

**Métricas:**
- Min, Max, Mean, Median
- P95, P99
- Requests/s

---

## 🛠️ Comandos Úteis

### Script de Desenvolvimento

```bash
# Inicia API
uv run python scripts/dev.py start

# Popula banco
uv run python scripts/dev.py seed

# Testes interativos
uv run python scripts/dev.py test

# Benchmark
uv run python scripts/dev.py benchmark

# Reseta banco
uv run python scripts/dev.py reset

# Mostra logs
uv run python scripts/dev.py logs

# Shell Python
uv run python scripts/dev.py shell
```

### Makefile

```bash
make install          # Instala dependências
make dev              # Inicia API (dev)
make seed             # Popula banco
make test-interactive # Testes interativos
make benchmark        # Benchmark
make reset            # Reseta banco
make logs             # Mostra logs
make shell            # Shell Python
```

---

## 🎓 Aprendendo

### 1. Leia a Documentação

```bash
# Documentação completa
ls backend/docs/

# Arquivos principais:
# - ARCHITECTURE.md  — Arquitetura
# - QUEUEFY.md       — Como o Queuefy funciona
# - DATABASE.md      — Modelo de banco
# - SERVICES.md      — Lógica de negócio
# - TESTING_GUIDE.md — Guia completo de testes
```

### 2. Explore o Código

```bash
# Estrutura
ls backend/src/app/

# Arquivos principais:
# - main.py      — Entry point
# - models.py    — Domain + DB models
# - services.py  — Business logic
# - routes.py    — API endpoints
# - queue.py     — Queuefy integration
# - ui.py        — NiceGUI pages
```

### 3. Teste no Shell Python

```bash
uv run python scripts/dev.py shell

# No shell:
task = await create_task('test', {'foo': 'bar'})
stats = await get_stats()
print(stats)
```

---

## 🐛 Troubleshooting

### API não inicia

```bash
# Verifica porta
lsof -i :8000

# Mata processo
kill -9 <PID>

# Inicia novamente
uv run python -m app.main
```

### Testes falham

```bash
# Verifica se API está rodando
curl http://localhost:8000/api/v1/health

# Se não estiver, inicia
uv run python -m app.main

# Executa testes
uv run python scripts/test_interactive.py
```

### Queuefy não processa

```bash
# Verifica logs da API
# Deve mostrar: "queuefy.started"

# Cria task e aguarda
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "payload": {}}'

sleep 2

# Verifica status
curl http://localhost:8000/api/v1/tasks/{task_id}
# Deve estar: "completed"
```

---

## 📚 Próximos Passos

1. ✅ Execute testes interativos: `uv run python scripts/test_interactive.py`
2. ✅ Acesse dashboard: http://localhost:8000/ui/
3. ✅ Veja documentação: http://localhost:8000/docs
4. ✅ Execute benchmark: `uv run python scripts/benchmark.py`
5. ✅ Leia docs em `backend/docs/`
6. ✅ Explore código em `backend/src/app/`

---

## 🎉 Parabéns!

Você testou todas as funcionalidades da POC! 🚀

**O que você aprendeu:**
- ✅ Como iniciar em desenvolvimento (SQLite)
- ✅ Como iniciar em produção (PostgreSQL)
- ✅ Como testar cada recurso
- ✅ Como medir performance
- ✅ Como debugar problemas

**Agora você pode:**
- 🎨 Customizar a aplicação
- 🧪 Adicionar novos testes
- 📊 Monitorar performance
- 🚀 Fazer deploy

**Divirta-se!** 🎊
