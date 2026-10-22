# 🗄️ Modelo de Banco de Dados

## Visão Geral

A aplicação usa **SQLAlchemy 2.0 async** com **SQLite** (ou PostgreSQL em produção).

## Tabelas

### 1. `tasks` — Suas Tasks de Negócio

```sql
CREATE TABLE tasks (
    id           VARCHAR(36) PRIMARY KEY,  -- UUID
    name         VARCHAR(255) NOT NULL,     -- Nome da task (ex: "send_email")
    payload      JSON,                      -- Dados da task (JSON)
    status       VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed/failed
    priority     VARCHAR(20) DEFAULT 'medium',   -- low/medium/high/critical
    queue        VARCHAR(100) DEFAULT 'default', -- Nome da fila
    attempts     INTEGER DEFAULT 0,              -- Quantas vezes tentou
    created_at   DATETIME,                       -- Quando foi criada
    started_at   DATETIME,                       -- Quando começou a processar
    completed_at DATETIME,                       -- Quando terminou
    error        VARCHAR(1000)                   -- Mensagem de erro (se falhou)
);

CREATE INDEX ix_tasks_name ON tasks(name);
CREATE INDEX ix_tasks_status ON tasks(status);
```

**Exemplo de dados:**

| id | name | status | priority | attempts | created_at |
|----|------|--------|----------|----------|------------|
| abc-123 | send_email | completed | high | 1 | 2026-01-15 10:30:00 |
| def-456 | process_image | running | medium | 0 | 2026-01-15 10:31:00 |
| ghi-789 | generate_report | pending | low | 0 | 2026-01-15 10:32:00 |

### 2. `queuefy_runs` — Executions do Queuefy

```sql
CREATE TABLE queuefy_runs (
    id           VARCHAR(36) PRIMARY KEY,
    task_name    VARCHAR(255) NOT NULL,  -- Qual handler executar
    task_id      VARCHAR(36),            -- ID da task (opcional)
    kwargs       JSON,                   -- Argumentos para o handler
    status       VARCHAR(20),            -- pending/running/completed/failed
    attempts     INTEGER,                -- Tentativas
    created_at   DATETIME,
    started_at   DATETIME,
    completed_at DATETIME,
    error        TEXT
);
```

**Exemplo de dados:**

| id | task_name | task_id | status | created_at |
|----|-----------|---------|--------|------------|
| run-001 | process_task | abc-123 | completed | 2026-01-15 10:30:00 |
| run-002 | send_notification | def-456 | running | 2026-01-15 10:31:00 |
| run-003 | daily_report | NULL | pending | 2026-01-15 04:00:00 |

### 3. `queuefy_schedules` — Cron Jobs

```sql
CREATE TABLE queuefy_schedules (
    task_name VARCHAR(255) PRIMARY KEY,
    cron      VARCHAR(100),      -- Expressão cron
    next_run  DATETIME,          -- Próxima execução
    last_run  DATETIME           -- Última execução
);
```

**Exemplo de dados:**

| task_name | cron | next_run | last_run |
|-----------|------|----------|----------|
| daily_report | 0 4 * * * | 2026-01-16 04:00:00 | 2026-01-15 04:00:00 |
| weekly_cleanup | 0 2 * * 0 | 2026-01-19 02:00:00 | 2026-01-12 02:00:00 |

## Modelos Python

### Task (Pydantic — modelo de domínio)

```python
# models.py
class Task(BaseModel):
    id: uuid.UUID
    name: str
    payload: dict
    status: TaskStatus      # PENDING, RUNNING, COMPLETED, FAILED
    priority: Priority      # LOW, MEDIUM, HIGH, CRITICAL
    queue: str
    attempts: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None
```

### TaskRow (SQLAlchemy — modelo de banco)

```python
# models.py
class TaskRow(Base):
    __tablename__ = "tasks"
    
    id: Mapped[str]
    name: Mapped[str]
    payload: Mapped[dict]
    status: Mapped[str]
    priority: Mapped[str]
    queue: Mapped[str]
    attempts: Mapped[int]
    created_at: Mapped[datetime]
    started_at: Mapped[datetime | None]
    completed_at: Mapped[datetime | None]
    error: Mapped[str | None]
    
    def to_task(self) -> Task:
        """Converte linha do banco para modelo de domínio."""
        ...
    
    @classmethod
    def from_task(cls, task: Task) -> "TaskRow":
        """Converte modelo de domínio para linha do banco."""
        ...
```

## Operações CRUD

### Criar Task

```python
async def create_task(name: str, payload: dict) -> Task:
    task = Task(name=name, payload=payload)
    session = await get_session()
    async with session:
        task = await save_task(session, task)
    return task
```

### Buscar Task

```python
async def get_task(task_id: uuid.UUID) -> Task | None:
    session = await get_session()
    async with session:
        return await get_task(session, task_id)
```

### Listar Tasks

```python
# Todas as tasks
tasks = await list_tasks(session)

# Filtrar por status
tasks = await list_tasks(session, status=TaskStatus.PENDING)

# Limitar quantidade
tasks = await list_tasks(session, limit=10)
```

### Atualizar Status

```python
async def execute_task(task_id: uuid.UUID):
    session = await get_session()
    async with session:
        task = await get_task(session, task_id)
        
        # Mark as running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        await save_task(session, task)
        
        # Process...
        
        # Mark as completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        await save_task(session, task)
```

## Consultas SQL Úteis

```sql
-- Ver todas as tasks
SELECT * FROM tasks ORDER BY created_at DESC;

-- Tasks pendentes
SELECT * FROM tasks WHERE status = 'pending';

-- Tasks que falharam
SELECT * FROM tasks WHERE status = 'failed';

-- Estatísticas por status
SELECT status, COUNT(*) as count 
FROM tasks 
GROUP BY status;

-- Tasks de alta prioridade
SELECT * FROM tasks 
WHERE priority = 'high' 
ORDER BY created_at DESC;

-- Tasks que tentaram muitas vezes
SELECT * FROM tasks 
WHERE attempts > 2 
ORDER BY attempts DESC;
```

## Conexão com Queuefy

O Queuefy usa as mesmas tabelas para gerenciar as execuções:

1. **tasks** — sua aplicação (modelo de negócio)
2. **queuefy_runs** — Queuefy (execuções dos handlers)
3. **queuefy_schedules** — Queuefy (cron jobs)

Quando você chama `enqueue()`:
- Insere uma linha em `queuefy_runs`
- O worker busca essa linha
- Executa o handler
- Atualiza o status

Quando o handler executa:
- Atualiza a task em `tasks`
- Atualiza a run em `queuefy_runs`

## Migração para PostgreSQL

Para produção, basta mudar a URL de conexão:

```python
# .env
POC_DB_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb
```

O código não muda — SQLAlchemy cuida da tradução SQL.

## Índices

Os índices são criados automaticamente pelo SQLAlchemy:

- `ix_tasks_name` — busca por nome
- `ix_tasks_status` — filtro por status

Para performance em produção, considere adicionar:

```sql
CREATE INDEX ix_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX ix_tasks_priority ON tasks(priority);
```
