# ⚙️ Services — Lógica de Negócio

## O que é?

O arquivo `services.py` contém a **lógica de negócio** da aplicação — as operações que a aplicação realiza, independentemente de como são chamadas (HTTP, CLI, queue, etc).

## Responsabilidades

### O que services.py FAZ

- ✅ Implementa casos de uso (use cases)
- ✅ Coordena operações de negócio
- ✅ Valida regras de negócio
- ✅ Chama repositórios (banco)
- ✅ Enfileira tasks (Queuefy)
- ✅ Retorna resultados

### O que services.py NÃO FAZ

- ❌ Não conhece HTTP (routes)
- ❌ Não conhece banco diretamente (database)
- ❌ Não conhece UI (NiceGUI)
- ❌ Não valida requests (routes faz isso)

## Estrutura

```python
# services.py
import uuid
from datetime import datetime
from app.database import get_session
from app.models import Task, TaskStatus, Priority, save_task, get_task, list_tasks, count_tasks

async def create_task(name: str, payload: dict | None = None, priority: Priority = Priority.MEDIUM) -> Task:
    """Cria uma nova task."""
    ...

async def execute_task(task_id: uuid.UUID) -> dict:
    """Executa uma task (chamado pelo worker)."""
    ...

async def get_task_by_id(task_id: uuid.UUID) -> Task | None:
    """Busca task por ID."""
    ...

async def get_all_tasks(status: TaskStatus | None = None, limit: int = 50) -> list[Task]:
    """Lista tasks."""
    ...

async def get_stats() -> dict:
    """Estatísticas de tasks."""
    ...
```

## Funções Principais

### create_task

**O que faz:**
1. Cria objeto Task
2. Salva no banco (status: pending)
3. Enfileira no Queuefy
4. Retorna task criada

```python
async def create_task(name: str, payload: dict | None = None, priority: Priority = Priority.MEDIUM) -> Task:
    """Cria uma nova task."""
    # 1. Cria objeto Task
    task = Task(name=name, payload=payload or {}, priority=priority)
    
    # 2. Salva no banco
    session = await get_session()
    async with session:
        task = await save_task(session, task)
    
    # 3. Enfileira no Queuefy
    await enqueue("process_task", task_id=str(task.id), payload=task.payload)
    
    # 4. Log
    await logger.ainfo("task.created", task_id=str(task.id), name=name)
    
    return task
```

**Fluxo:**
```
create_task()
    ↓
Task(name, payload)
    ↓
save_task(session, task) → banco (tasks table)
    ↓
enqueue("process_task") → Queuefy (queuefy_runs table)
    ↓
return task
```

### execute_task

**O que faz:**
1. Busca task no banco
2. Marca como running
3. Processa (simula trabalho)
4. Marca como completed
5. Retorna resultado

```python
async def execute_task(task_id: uuid.UUID) -> dict:
    """Executa uma task (chamado pelo worker do Queuefy)."""
    session = await get_session()
    async with session:
        # 1. Busca task
        task = await get_task(session, task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # 2. Mark as running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        task.attempts += 1
        await save_task(session, task)
        
        # 3. Process (simula trabalho async)
        import asyncio
        await asyncio.sleep(0.1)
        
        # 4. Mark as completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        await save_task(session, task)
    
    # 5. Log
    await logger.ainfo("task.completed", task_id=str(task_id))
    
    return {"success": True, "task_id": str(task_id)}
```

**Fluxo:**
```
execute_task(task_id)
    ↓
get_task(session, task_id) → busca no banco
    ↓
task.status = RUNNING
    ↓
save_task(session, task) → atualiza banco
    ↓
await asyncio.sleep(0.1) → processa
    ↓
task.status = COMPLETED
    ↓
save_task(session, task) → atualiza banco
    ↓
return {"success": True}
```

### get_task_by_id

**O que faz:**
- Busca task por ID
- Retorna Task ou None

```python
async def get_task_by_id(task_id: uuid.UUID) -> Task | None:
    """Busca task por ID."""
    session = await get_session()
    async with session:
        return await get_task(session, task_id)
```

### get_all_tasks

**O que faz:**
- Lista tasks
- Opcionalmente filtra por status
- Limita quantidade

```python
async def get_all_tasks(status: TaskStatus | None = None, limit: int = 50) -> list[Task]:
    """Lista tasks."""
    session = await get_session()
    async with session:
        return await list_tasks(session, status=status, limit=limit)
```

**Exemplos:**
```python
# Todas as tasks
tasks = await get_all_tasks()

# Só tasks pendentes
tasks = await get_all_tasks(status=TaskStatus.PENDING)

# Limitar a 10
tasks = await get_all_tasks(limit=10)
```

### get_stats

**O que faz:**
- Conta tasks por status
- Retorna estatísticas

```python
async def get_stats() -> dict:
    """Estatísticas de tasks."""
    session = await get_session()
    async with session:
        return await count_tasks(session)
```

**Retorna:**
```python
{
    "total": 100,
    "pending": 10,
    "running": 5,
    "completed": 80,
    "failed": 5
}
```

## Padrões de Design

### 1. Session Management

```python
# ✅ Correto — session é fechada automaticamente
async def my_service():
    session = await get_session()
    async with session:
        task = await get_task(session, task_id)
        return task

# ❌ Errado — session não é fechada
async def my_service():
    session = await get_session()
    task = await get_task(session, task_id)
    return task  # session vazou!
```

### 2. Error Handling

```python
# ✅ Correto — trata erros
async def execute_task(task_id: uuid.UUID) -> dict:
    session = await get_session()
    async with session:
        task = await get_task(session, task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        try:
            # Process
            ...
            return {"success": True}
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            await save_task(session, task)
            return {"success": False, "error": str(e)}

# ❌ Errado — não trata erros
async def execute_task(task_id: uuid.UUID):
    session = await get_session()
    task = await get_task(session, task_id)
    # Process — pode crashar!
```

### 3. Logging

```python
# ✅ Correto — log estruturado
async def create_task(name: str, payload: dict):
    task = Task(name=name, payload=payload)
    session = await get_session()
    async with session:
        task = await save_task(session, task)
    
    await logger.ainfo("task.created", task_id=str(task.id), name=name)
    return task

# ❌ Errado — print ou log sem contexto
async def create_task(name: str, payload: dict):
    task = Task(name=name, payload=payload)
    print(f"Created task: {task.id}")  # Não use print!
    return task
```

### 4. Async First

```python
# ✅ Correto — tudo async
async def create_task(name: str) -> Task:
    task = Task(name=name)
    session = await get_session()
    async with session:
        task = await save_task(session, task)
    return task

# ❌ Errado — sync bloqueia o event loop
def create_task(name: str) -> Task:  # sync!
    task = Task(name=name)
    session = get_session()  # bloqueia!
    task = save_task(session, task)  # bloqueia!
    return task
```

## Casos de Uso Comuns

### Criar e processar task

```python
# routes.py
@router.post("/tasks")
async def create_task_endpoint(req: CreateTaskRequest):
    task = await create_task(
        name=req.name,
        payload=req.payload,
        priority=req.priority
    )
    return TaskResponse.from_task(task)

# services.py
async def create_task(name: str, payload: dict, priority: Priority) -> Task:
    task = Task(name=name, payload=payload, priority=priority)
    session = await get_session()
    async with session:
        task = await save_task(session, task)
    await enqueue("process_task", task_id=str(task.id))
    return task
```

### Processar task em background

```python
# queue.py (handler do Queuefy)
@_queuefy.task("process_task")
async def handle_process_task(task_id: str, payload: dict):
    result = await execute_task(uuid.UUID(task_id))
    return result

# services.py
async def execute_task(task_id: uuid.UUID) -> dict:
    session = await get_session()
    async with session:
        task = await get_task(session, task_id)
        task.status = TaskStatus.RUNNING
        await save_task(session, task)
        
        # Process
        await asyncio.sleep(0.1)
        
        task.status = TaskStatus.COMPLETED
        await save_task(session, task)
    
    return {"success": True}
```

### Listar tasks com filtro

```python
# routes.py
@router.get("/tasks")
async def list_tasks_endpoint(status: TaskStatus | None = None, limit: int = 50):
    tasks = await get_all_tasks(status=status, limit=limit)
    return [TaskResponse.from_task(t) for t in tasks]

# services.py
async def get_all_tasks(status: TaskStatus | None = None, limit: int = 50) -> list[Task]:
    session = await get_session()
    async with session:
        return await list_tasks(session, status=status, limit=limit)
```

### Obter estatísticas

```python
# routes.py
@router.get("/tasks/stats")
async def get_stats_endpoint():
    return await get_stats()

# services.py
async def get_stats() -> dict:
    session = await get_session()
    async with session:
        return await count_tasks(session)
```

## Testando Services

### Mock do banco

```python
# tests/test_services.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services import create_task

@pytest.mark.asyncio
async def test_create_task():
    with patch("app.services.get_session") as mock_get_session:
        mock_session = AsyncMock()
        mock_get_session.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        
        with patch("app.services.save_task") as mock_save:
            mock_save.return_value = Task(id=uuid.uuid4(), name="test")
            
            with patch("app.services.enqueue") as mock_enqueue:
                task = await create_task(name="test", payload={"foo": "bar"})
                
                assert task.name == "test"
                mock_save.assert_called_once()
                mock_enqueue.assert_called_once()
```

### Teste de integração

```python
@pytest.mark.asyncio
async def test_create_task_integration():
    # Usa banco real (SQLite em memória)
    from app.database import init_db, get_session
    
    await init_db("sqlite+aiosqlite:///:memory:")
    
    task = await create_task(name="test", payload={"foo": "bar"})
    
    assert task.name == "test"
    assert task.status == TaskStatus.PENDING
    
    # Verifica no banco
    session = await get_session()
    async with session:
        db_task = await get_task(session, task.id)
        assert db_task is not None
        assert db_task.name == "test"
```

## Quando Adicionar Nova Função

### Adicione quando:

- ✅ Nova operação de negócio
- ✅ Nova regra de negócio
- ✅ Nova validação de domínio
- ✅ Nova coordenação de operações

### NÃO adicione quando:

- ❌ É só HTTP (vai para routes)
- ❌ É só banco (vai para models/database)
- ❌ É só UI (vai para ui)
- ❌ É só fila (vai para queue)

## Exemplo: Adicionar nova operação

### Cenário: Cancelar task

```python
# services.py
async def cancel_task(task_id: uuid.UUID) -> Task | None:
    """Cancela uma task pendente."""
    session = await get_session()
    async with session:
        task = await get_task(session, task_id)
        if not task:
            return None
        
        # Só pode cancelar se estiver pendente
        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot cancel task in status: {task.status}")
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        await save_task(session, task)
        
        await logger.ainfo("task.cancelled", task_id=str(task_id))
        return task
```

### Usando em routes

```python
# routes.py
@router.post("/tasks/{task_id}/cancel")
async def cancel_task_endpoint(task_id: uuid.UUID):
    task = await cancel_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return TaskResponse.from_task(task)
```

## Conclusão

`services.py` é o **coração da aplicação** — contém toda a lógica de negócio. Mantenha-o:

- ✅ Simples e direto
- ✅ Async first
- ✅ Bem testado
- ✅ Bem documentado
- ✅ Sem dependências de HTTP/UI
