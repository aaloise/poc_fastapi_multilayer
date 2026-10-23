# 🎯 Como Tudo Funciona Junto

## Visão Geral

A aplicação tem **3 componentes principais** que trabalham juntos:

```
┌─────────────────────────────────────────────────────────┐
│                    Navegador                              │
│              http://localhost:8000                       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐         ┌──────────────┐
│  /ui/        │         │  /api/v1/    │
│  NiceGUI     │         │  FastAPI     │
│  Dashboard   │         │  REST API    │
└──────┬───────┘         └──────┬───────┘
       │                        │
       └────────┬───────────────┘
                │
                ▼
       ┌────────────────┐
       │   services.py  │
       │  Business      │
       │  Logic         │
       └────────┬───────┘
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  database.py │  │  queue.py    │
│  SQLite/     │  │  Queuefy     │
│  PostgreSQL  │  │  Task Queue  │
└──────────────┘  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   Worker     │
                  │  (background)│
                  └──────────────┘
```

## Fluxo Completo

### 1. Criar Task via Dashboard

```
Usuário → Dashboard (/ui/) → API (/api/v1/tasks) → services.py
                                                         ↓
                                                    database.py (salva)
                                                         ↓
                                                    queue.py (enfileira)
                                                         ↓
                                                    Worker processa
                                                         ↓
                                                    database.py (atualiza status)
```

### 2. Criar Task via API

```
curl POST /api/v1/tasks → services.py → database.py + queue.py
                                              ↓
                                         Worker processa
                                              ↓
                                         database.py (atualiza)
```

### 3. Worker Processa Task

```
Queuefy detecta task pendente
       ↓
Chama handler (queue.py)
       ↓
Handler chama services.execute_task()
       ↓
services.py processa
       ↓
database.py atualiza status
```

## Arquivos e Responsabilidades

### main.py
- **O que faz:** Inicia tudo (API + UI + Queue)
- **Quando usar:** Sempre (é o único entry point)
- **O que inicia:**
  - FastAPI app
  - NiceGUI dashboard
  - Database connection
  - Queuefy worker

### config.py
- **O que faz:** Gerencia configurações
- **Ambientes:**
  - `development` - SQLite local, debug on
  - `production` - PostgreSQL, debug off
  - `testing` - SQLite em memória

### models.py
- **O que faz:** Define estruturas de dados
- **Contém:**
  - `Task` - Modelo de domínio (Pydantic)
  - `TaskRow` - Modelo de banco (SQLAlchemy)
  - `TaskStatus` - Enum de status
  - `Priority` - Enum de prioridade

### services.py
- **O que faz:** Lógica de negócio
- **Funções:**
  - `create_task()` - Cria e enfileira task
  - `execute_task()` - Processa task
  - `get_task_by_id()` - Busca task
  - `get_all_tasks()` - Lista tasks
  - `get_stats()` - Estatísticas

### routes.py
- **O que faz:** Endpoints HTTP
- **Endpoints:**
  - `POST /api/v1/tasks` - Criar task
  - `GET /api/v1/tasks` - Listar tasks
  - `GET /api/v1/tasks/{id}` - Buscar task
  - `GET /api/v1/tasks/stats` - Estatísticas
  - `GET /api/v1/health` - Health check

### ui.py
- **O que faz:** Dashboard visual
- **Páginas:**
  - `/ui/` - Dashboard principal
  - `/ui/architecture` - Diagrama da arquitetura
  - `/ui/monitor` - Monitor em tempo real

### queue.py
- **O que faz:** Fila de tarefas
- **Handlers:**
  - `process_task` - Processa task genérica
  - `send_notification` - Envia notificação
  - `daily_report` - Relatório diário (cron)
  - `weekly_cleanup` - Limpeza semanal (cron)

### database.py
- **O que faz:** Gerencia banco de dados
- **Funções:**
  - `init_db()` - Inicializa conexão
  - `get_session()` - Retorna session
  - `close_db()` - Fecha conexão

### flows.py
- **O que faz:** Workflows Prefect (opcional)
- **Flows:**
  - `data_pipeline` - Pipeline ETL
  - `batch_process` - Processamento em lote

## Ambientes

### Development (padrão)

```bash
uv run python -m app.main
```

- **Banco:** SQLite (dev_poc.db)
- **Debug:** On
- **Workers:** 4
- **Log:** DEBUG
- **Host:** 127.0.0.1

### Production

```bash
POC_ENV=production uv run python -m app.main
```

- **Banco:** PostgreSQL
- **Debug:** Off
- **Workers:** 8
- **Log:** WARNING
- **Host:** 0.0.0.0

### Testing

```bash
POC_ENV=testing pytest
```

- **Banco:** SQLite em memória
- **Debug:** On
- **Workers:** 2
- **Log:** ERROR

## Testando

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Verifica se todos os componentes estão funcionando.

### 2. Criar Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "payload": {"foo": "bar"}}'
```

Cria task e enfileira para processamento.

### 3. Listar Tasks

```bash
curl http://localhost:8000/api/v1/tasks
```

Mostra todas as tasks (incluindo as que o worker processou).

### 4. Verificar Processamento

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

O status deve mudar de `pending` para `completed` após 1-2 segundos.

### 5. Dashboard

Abra http://localhost:8000/ui/ no navegador.

Mostra tasks em tempo real, permite criar novas tasks, ver estatísticas.

## Queuefy em Ação

### Como funciona:

1. **Task criada** → `services.create_task()`
2. **Salva no banco** → status: `pending`
3. **Enfileira** → `queue.enqueue()`
4. **Worker detecta** → Queuefy monitora banco
5. **Worker processa** → Chama handler
6. **Atualiza status** → status: `completed`

### Ver nos logs:

```
INFO:queuefy.enqueued task_name=process_task task_id=abc-123
INFO:queuefy.handler.process_task task_id=abc-123
INFO:task.completed task_id=abc-123
```

## Cron Jobs

Tasks agendadas rodam automaticamente:

```python
@_queuefy.task("daily_report", cron="0 4 * * *")
async def handle_daily_report():
    # Roda todo dia às 4h da manhã
    ...
```

### Ver cron jobs:

```sql
SELECT * FROM queuefy_schedules;
```

## Banco de Dados

### Tabelas

1. **tasks** - Suas tasks
2. **queuefy_runs** - Execuções do Queuefy
3. **queuefy_schedules** - Cron jobs

### Ver dados:

```bash
# SQLite
sqlite3 dev_poc.db
SELECT * FROM tasks;
SELECT * FROM queuefy_runs;

# PostgreSQL
docker exec -it poc-postgres psql -U poc -d poc_prod
SELECT * FROM tasks;
```

## Performance

### Métricas

```bash
uv run python scripts/benchmark.py
```

Mostra:
- Latência (min, max, avg, P95, P99)
- Throughput (requests/s)
- Performance por endpoint

### Otimizações

- **uvloop** - Event loop rápido (Linux/Mac)
- **async/await** - Não-bloqueante
- **Connection pooling** - Reutiliza conexões
- **Worker pool** - Processa em paralelo

## Troubleshooting

### Task não processa

1. Verifique se worker está rodando (logs mostram `queuefy.started`)
2. Verifique se task foi enfileirada (logs mostram `queuefy.enqueued`)
3. Verifique status no banco (`SELECT * FROM tasks WHERE id = '...'`)

### Dashboard não carrega

1. Verifique se servidor está rodando
2. Acesse http://localhost:8000/ui/
3. Verifique logs do servidor

### API não responde

1. Verifique se servidor está rodando
2. Teste health check: `curl http://localhost:8000/api/v1/health`
3. Verifique logs do servidor

## Próximos Passos

1. ✅ Execute `GUIA_RAPIDO.md`
2. ✅ Teste o dashboard
3. ✅ Execute `test_interactive.py`
4. ✅ Execute `benchmark.py`
5. ✅ Leia `docs/QUEUEFY.md`
6. ✅ Modifique o código e experimente!
