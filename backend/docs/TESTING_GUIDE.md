# 🧪 Guia de Testes — Passo a Passo

Este guia mostra como testar **todas** as funcionalidades da POC de forma metódica e didática.

## 📋 Índice

1. [Ambiente de Desenvolvimento](#1-ambiente-de-desenvolvimento)
2. [Ambiente de Produção](#2-ambiente-de-produção)
3. [Testes Interativos](#3-testes-interativos)
4. [Dashboard de Testes](#4-dashboard-de-testes)
5. [Benchmark de Performance](#5-benchmark-de-performance)
6. [Testando Cada Recurso](#6-testando-cada-recurso)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Ambiente de Desenvolvimento

### Setup Rápido

```bash
cd backend

# Instala dependências
uv sync

# Popula banco com dados de exemplo
uv run python scripts/seed_data.py

# Inicia a API
uv run python -m app.main
```

### O que acontece?

1. ✅ Cria arquivo `dev_poc.db` (SQLite local)
2. ✅ Cria tabelas automaticamente
3. ✅ Popula com 10 tasks de exemplo
4. ✅ Inicia servidor em `http://localhost:8000`
5. ✅ Worker do Queuefy inicia em background

### Verificando

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Deve retornar:
{
    "status": "healthy",
    "version": "0.1.0",
    "components": {
        "fastapi": true,
        "database": true,
        "queuefy": true,
        "prefect": true,
        "nicegui": true,
        "uvloop": true
    }
}
```

### Acessando

- **API**: http://localhost:8000/api/v1/
- **Dashboard**: http://localhost:8000/ui/
- **Tests**: http://localhost:8000/ui/tests
- **Docs**: http://localhost:8000/docs

---

## 2. Ambiente de Produção

### Setup com PostgreSQL

```bash
# Executa script de setup
chmod +x scripts/setup_production.sh
./scripts/setup_production.sh
```

### O que acontece?

1. ✅ Inicia PostgreSQL via Docker
2. ✅ Cria banco `poc_prod`
3. ✅ Cria arquivo `.env.production`
4. ✅ Popula banco com dados
5. ✅ Configura para produção

### Iniciando

```bash
# Com uvicorn (simples)
POC_ENV=production uv run python -m app.main

# Com Granian (recomendado)
POC_ENV=production uv run granian --interface asgi app.main:app
```

### Verificando PostgreSQL

```bash
# Conecta ao banco
docker exec -it poc-postgres psql -U poc -d poc_prod

# Lista tabelas
\dt

# Mostra tasks
SELECT * FROM tasks LIMIT 5;

# Mostra queuefy runs
SELECT * FROM queuefy_runs LIMIT 5;

# Sai
\q
```

---

## 3. Testes Interativos

### Executando

```bash
uv run python scripts/test_interactive.py
```

### O que testa?

1. ✅ **Health Check** — API está rodando?
2. ✅ **Create Task** — Cria task simples
3. ✅ **Create Multiple Tasks** — Cria 5 tasks com prioridades diferentes
4. ✅ **List Tasks** — Lista todas as tasks
5. ✅ **Get Task by ID** — Busca task específica
6. ✅ **Get Stats** — Estatísticas das tasks
7. ✅ **Queuefy Integration** — Worker processou a task?
8. ✅ **Prefect Flow** — Pipeline do Prefect funciona?
9. ✅ **NiceGUI UI** — Dashboard está acessível?
10. ✅ **Error Handling** — Retorna 404 para task inexistente?

### Saída esperada

```
🚀 Async POC — Teste Interativo Completo

🏥 Teste 1: Health Check
Step 1: Verificando se a API está rodando...
✓ API está saudável!

┌─────────────────┬────────┐
│ Componente      │ Status │
├─────────────────┼────────┤
│ fastapi         │ ✓ OK   │
│ database        │ ✓ OK   │
│ queuefy         │ ✓ OK   │
│ prefect         │ ✓ OK   │
│ nicegui         │ ✓ OK   │
│ uvloop          │ ✓ OK   │
└─────────────────┴────────┘

... (mais testes)

📊 Resumo dos Testes

┌──────────────────────┬────────┬──────────┬──────────┐
│ Teste                │ Status │ Duração  │ Detalhes │
├──────────────────────┼────────┼──────────┼──────────┤
│ Health Check         │ ✓ PASS │ 0.012s   │          │
│ Create Task          │ ✓ PASS │ 0.045s   │ abc-123  │
│ Create Multiple      │ ✓ PASS │ 0.234s   │          │
│ List Tasks           │ ✓ PASS │ 0.023s   │ 15 tasks │
│ Get Task by ID       │ ✓ PASS │ 0.015s   │          │
│ Get Stats            │ ✓ PASS │ 0.018s   │          │
│ Queuefy Integration  │ ✓ PASS │ 2.012s   │ completed│
│ Prefect Flow         │ ✓ PASS │ 1.234s   │          │
│ NiceGUI UI           │ ✓ PASS │ 0.034s   │          │
│ Error Handling       │ ✓ PASS │ 0.011s   │          │
└──────────────────────┴────────┴──────────┴──────────┘

Total: 10 testes
Passou: 10
Falhou: 0
Tempo total: 3.72s

🎉 Todos os testes passaram!
```

---

## 4. Dashboard de Testes

### Acessando

1. Inicie a API: `uv run python -m app.main`
2. Acesse: http://localhost:8000/ui/tests

### O que mostra?

- ✅ Status de cada teste em tempo real
- ✅ Logs de execução
- ✅ Botões para executar testes individuais
- ✅ Botão para executar todos os testes
- ✅ Resumo com tabela de resultados

### Como usar?

1. Clique em **"Executar Todos os Testes"**
2. Aguarde cada teste executar
3. Veja o status mudar de "⏳ Executando..." para "✓ Passou" ou "✗ Falhou"
4. Veja os logs de cada teste
5. Clique em **"Atualizar Resumo"** para ver a tabela

---

## 5. Benchmark de Performance

### Executando

```bash
# Benchmark básico (10 requests por teste)
uv run python scripts/benchmark.py

# Benchmark intenso (100 requests por teste)
uv run python scripts/benchmark.py --requests 100
```

### O que mede?

1. ✅ **Health Check** — Latência do endpoint de health
2. ✅ **Create Task** — Performance de criação de tasks
3. ✅ **List Tasks** — Performance de listagem
4. ✅ **Get Task by ID** — Performance de busca
5. ✅ **Get Stats** — Performance de estatísticas

### Métricas

- **Min** — Menor tempo
- **Max** — Maior tempo
- **Mean** — Tempo médio
- **Median** — Mediana
- **Std Dev** — Desvio padrão
- **P95** — 95º percentil (se ≥20 requests)
- **P99** — 99º percentil (se ≥100 requests)
- **Requests/s** — Requests por segundo

### Saída esperada

```
⚡ Async POC — Benchmark
Iterations per test: 10

Test: Health Check
Iterations: 10
┌─────────────┬──────────┐
│ Metric      │ Value    │
├─────────────┼──────────┤
│ Min         │ 2.34ms   │
│ Max         │ 15.67ms  │
│ Mean        │ 5.12ms   │
│ Median      │ 4.89ms   │
│ Std Dev     │ 3.45ms   │
│ Total       │ 0.05s    │
│ Requests/s  │ 195.3    │
└─────────────┴──────────┘

... (mais testes)

📊 Benchmark Summary

┌──────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Test         │ Requests │ Avg Time │ Min      │ Max      │ Req/s    │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Health Check │ 10       │ 5.12ms   │ 2.34ms   │ 15.67ms  │ 195.3    │
│ Create Task  │ 10       │ 45.23ms  │ 38.12ms  │ 67.89ms  │ 22.1     │
│ List Tasks   │ 10       │ 23.45ms  │ 18.23ms  │ 34.56ms  │ 42.6     │
│ Get Task     │ 10       │ 12.34ms  │ 8.45ms   │ 23.67ms  │ 81.0     │
│ Get Stats    │ 10       │ 18.90ms  │ 14.23ms  │ 28.45ms  │ 52.9     │
└──────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

✓ Benchmark completo!
```

---

## 6. Testando Cada Recurso

### 6.1 FastAPI Routes

#### Criar Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_email",
    "payload": {"to": "user@example.com", "subject": "Hello"},
    "priority": "high"
  }'
```

#### Listar Tasks

```bash
curl http://localhost:8000/api/v1/tasks

# Com filtro
curl "http://localhost:8000/api/v1/tasks?status=pending&limit=10"
```

#### Buscar Task

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

#### Estatísticas

```bash
curl http://localhost:8000/api/v1/tasks/stats
```

### 6.2 Queuefy (Task Queue)

#### Verificar se worker está rodando

```bash
# Crie uma task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "test_queuefy", "payload": {}}'

# Aguarde 2 segundos
sleep 2

# Verifique o status
curl http://localhost:8000/api/v1/tasks/{task_id}

# Deve mostrar status: "completed" ou "running"
```

#### Ver logs do Queuefy

```bash
# No console onde a API está rodando, você verá:
# INFO:queuefy.started concurrency=4
# INFO:queuefy.enqueued task_name=process_task task_id=abc-123
# INFO:queuefy.handler.process_task task_id=abc-123
# INFO:task.completed task_id=abc-123
```

### 6.3 Prefect Flows

#### Executar pipeline

```bash
curl -X POST "http://localhost:8000/api/v1/flows/pipeline?source=test_api"
```

#### Ver logs do Prefect

```bash
# No console:
# INFO:prefect.flow.data_pipeline Pipeline starting: test_api
# INFO:prefect.task.fetch_data Fetching from test_api
# INFO:prefect.task.transform_data Transforming data
# INFO:prefect.flow.data_pipeline Pipeline done: {...}
```

### 6.4 NiceGUI Dashboard

#### Acessar dashboard

```bash
# Abra no navegador
http://localhost:8000/ui/
```

#### O que ver?

- ✅ Stats cards (Total, Pending, Completed)
- ✅ Formulário para criar task
- ✅ Tabela com tasks recentes
- ✅ Botão de refresh

### 6.5 Database

#### SQLite (Dev)

```bash
# Conecta ao banco
sqlite3 dev_poc.db

# Lista tabelas
.tables

# Mostra tasks
SELECT * FROM tasks LIMIT 5;

# Mostra queuefy runs
SELECT * FROM queuefy_runs LIMIT 5;

# Sai
.quit
```

#### PostgreSQL (Prod)

```bash
# Conecta ao banco
docker exec -it poc-postgres psql -U poc -d poc_prod

# Lista tabelas
\dt

# Mostra tasks
SELECT id, name, status, priority, created_at FROM tasks ORDER BY created_at DESC LIMIT 5;

# Estatísticas
SELECT status, COUNT(*) FROM tasks GROUP BY status;

# Sai
\q
```

---

## 7. Troubleshooting

### API não inicia

```bash
# Verifica se porta está em uso
lsof -i :8000

# Mata processo
kill -9 <PID>

# Ou usa outra porta
POC_PORT=8001 uv run python -m app.main
```

### Queuefy não processa tasks

```bash
# Verifica logs da API
# Deve mostrar: "queuefy.started"

# Verifica se worker está rodando
# Crie uma task e aguarde 5 segundos
# Verifique se status mudou para "completed"
```

### PostgreSQL não conecta

```bash
# Verifica se container está rodando
docker ps | grep poc-postgres

# Se não estiver, inicia
docker start poc-postgres

# Verifica se banco existe
docker exec -it poc-postgres psql -U poc -c "\l"

# Se não existir, recria
docker exec -it poc-postgres createdb -U poc poc_prod
```

### Testes falham

```bash
# Verifica se API está rodando
curl http://localhost:8000/api/v1/health

# Se não estiver, inicia
uv run python -m app.main

# Executa testes novamente
uv run python scripts/test_interactive.py
```

### Benchmark lento

```bash
# Reduz número de requests
uv run python scripts/benchmark.py --requests 5

# Verifica se há outros processos rodando
top

# Verifica uso de CPU/RAM
htop
```

---

## 📚 Próximos Passos

1. ✅ Execute todos os testes: `uv run python scripts/test_interactive.py`
2. ✅ Acesse o dashboard: http://localhost:8000/ui/
3. ✅ Veja a documentação: http://localhost:8000/docs
4. ✅ Execute o benchmark: `uv run python scripts/benchmark.py`
5. ✅ Leia os docs em `backend/docs/`

---

## 🎉 Parabéns!

Você testou todas as funcionalidades da POC! 🚀

Agora você sabe:
- ✅ Como iniciar em desenvolvimento (SQLite)
- ✅ Como iniciar em produção (PostgreSQL)
- ✅ Como testar cada recurso
- ✅ Como medir performance
- ✅ Como debugar problemas

**Divirta-se explorando!** 🎊
