# 📊 Como o Queuefy Funciona

## O que é Queuefy?

Queuefy é uma **task queue** que usa o **próprio banco de dados** para armazenar as tasks. Não precisa de Redis, RabbitMQ ou outro broker externo.

## Fluxo Completo

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
   (em ambas as tabelas: tasks e queuefy_runs)
```

## Tabelas no Banco

### 1. `tasks` (sua aplicação)

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

**O que armazena:**
- Suas tasks de negócio (ex: "send_email", "process_image")
- Status atual (pending/running/completed/failed)
- Dados da task (payload em JSON)
- Quantas vezes tentou processar (attempts)

### 2. `queuefy_runs` (Queuefy)

```sql
CREATE TABLE queuefy_runs (
    id           VARCHAR(36) PRIMARY KEY,
    task_name    VARCHAR(255) NOT NULL,
    task_id      VARCHAR(36),
    kwargs       JSON,
    status       VARCHAR(20),
    attempts     INTEGER,
    created_at   DATETIME,
    started_at   DATETIME,
    completed_at DATETIME,
    error        TEXT
);
```

**O que armazena:**
- As "runs" do Queuefy (execuções de tasks)
- Qual handler executar (task_name)
- Argumentos para o handler (kwargs)
- Status da execução

### 3. `queuefy_schedules` (Queuefy)

```sql
CREATE TABLE queuefy_schedules (
    task_name VARCHAR(255) PRIMARY KEY,
    cron      VARCHAR(100),
    next_run  DATETIME,
    last_run  DATETIME
);
```

**O que armazena:**
- Tasks agendadas com cron (ex: "0 4 * * *" = todo dia às 4h)
- Quando é a próxima execução
- Quando foi a última execução

## Como Usar

### 1. Task Imediata

```python
# services.py
async def create_task(name: str, payload: dict):
    # 1. Cria task no banco (tabela: tasks)
    task = Task(name=name, payload=payload)
    session = await get_session()
    task = await save_task(session, task)
    
    # 2. Enfileira no Queuefy (tabela: queuefy_runs)
    await enqueue("process_task", task_id=str(task.id), payload=payload)
    
    return task
```

### 2. Handler Registrado

```python
# queue.py
@_queuefy.task("process_task", max_attempts=3, timeout=60)
async def handle_process_task(task_id: str, payload: dict) -> dict:
    """
    Este handler é executado pelo worker quando uma task
    com task_name="process_task" é enfileirada.
    """
    from app.services import execute_task
    
    # Executa a lógica de negócio
    result = await execute_task(uuid.UUID(task_id))
    
    return result
```

### 3. Cron Job (Task Agendada)

```python
# queue.py
@_queuefy.task("daily_report", cron="0 4 * * *")
async def handle_daily_report() -> dict:
    """
    Esta task roda automaticamente todos os dias às 4h da manhã.
    O Queuefy cria as "runs" automaticamente baseado no cron.
    """
    from app.services import get_stats
    stats = await get_stats()
    return {"report": stats}
```

### 4. Task Agendada para Horário Específico

```python
from datetime import datetime, timedelta

# Rodar daqui a 1 hora
await enqueue_at(
    "send_notification",
    when=datetime.utcnow() + timedelta(hours=1),
    message="Hello!",
    channel="email"
)
```

## Worker em Background

O worker é iniciado no `main.py` durante o startup:

```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db(settings.db_url)
    await init_queue(_engine, settings.queue_concurrency)
    yield
    # Shutdown
    await stop_queue()
    await close_db()
```

O worker:
1. Fica rodando em background (asyncio.create_task)
2. Busca tasks pendentes na tabela `queuefy_runs`
3. Executa o handler correspondente
4. Atualiza o status para completed/failed
5. Repete o processo

## Vantagens

✅ **Zero dependências externas** — usa o mesmo banco da aplicação  
✅ **100% Async** — integra perfeitamente com FastAPI e uvloop  
✅ **Retry automático** — tenta novamente se falhar (configurável)  
✅ **Cron jobs nativos** — agendamento com expressões cron  
✅ **Multi-worker safe** — vários workers sem duplicar tasks  
✅ **Simples de usar** — API minimalista: `enqueue()` e `@task`

## Exemplo Completo

```python
# 1. Criar task via API
POST /api/v1/tasks
{
    "name": "send_email",
    "payload": {"to": "user@example.com", "subject": "Hello"}
}

# 2. Internamente:
# - Cria linha em tasks (status: pending)
# - Cria linha em queuefy_runs (status: pending)

# 3. Worker pega a task
# - Busca queuefy_runs onde status='pending'
# - Encontra task_name="process_task"
# - Executa handle_process_task()

# 4. Handler executa
# - Chama execute_task(task_id)
# - Processa a lógica de negócio
# - Atualiza tasks (status: completed)
# - Atualiza queuefy_runs (status: completed)

# 5. Resultado
# - Task processada com sucesso
# - Ambas as tabelas atualizadas
```

## Consultando o Banco

```sql
-- Ver todas as tasks
SELECT * FROM tasks ORDER BY created_at DESC;

-- Ver tasks pendentes
SELECT * FROM tasks WHERE status = 'pending';

-- Ver runs do Queuefy
SELECT * FROM queuefy_runs ORDER BY created_at DESC;

-- Ver schedules (cron jobs)
SELECT * FROM queuefy_schedules;

-- Estatísticas
SELECT status, COUNT(*) FROM tasks GROUP BY status;
```

## Links

- [Queuefy no GitHub](https://github.com/paulocoutinhox/queuefy)
- [Queuefy no PyPI](https://pypi.org/project/queuefy/)
- [Documentação](https://github.com/paulocoutinhox/queuefy/blob/main/README.md)
