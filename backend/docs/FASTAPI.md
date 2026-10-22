# ⚡ FastAPI — Framework HTTP

## O que é?

FastAPI é um **framework web moderno e ultra-rápido** para construir APIs com Python 3.7+, baseado em type hints e Starlette.

## Por que FastAPI?

### Comparação com outros frameworks

| Framework | Performance | Async | Type Hints | Docs Auto |
|-----------|-------------|-------|------------|-----------|
| **Flask** | Média | ❌ | ❌ | ❌ |
| **Django** | Média | Parcial | ❌ | ❌ |
| **FastAPI** | **Excelente** | **✅** | **✅** | **✅** |

### Vantagens

1. **Performance** — Tão rápido quanto Node.js e Go
2. **Async/Await** — Suporte nativo a async
3. **Type Hints** — Validação automática com Pydantic
4. **Documentação** — Swagger UI e ReDoc automáticos
5. **Dependency Injection** — Sistema poderoso
6. **Baseado em padrões** — OpenAPI, JSON Schema

## Instalação

```bash
# Com uv
uv add fastapi pydantic pydantic-settings

# Com pip
pip install fastapi pydantic pydantic-settings
```

## Estrutura Básica

### Criando a aplicação

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="Async POC",
    version="0.1.0",
    description="POC com FastAPI + Granian + Queuefy"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Executando

```bash
# Desenvolvimento (com reload)
uv run python -m app.main

# Produção (com Granian)
uv run granian --interface asgi app.main:app
```

## Lifespan (Startup/Shutdown)

### O que é?

Lifespan é o ciclo de vida da aplicação — o que acontece quando ela inicia e para.

### Exemplo

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown."""
    # Startup
    await init_db(settings.db_url)
    await init_queue(_engine, settings.queue_concurrency)
    
    yield  # Aplicação rodando
    
    # Shutdown
    await stop_queue()
    await close_db()

app = FastAPI(title="Async POC", lifespan=lifespan)
```

### Ordem de Execução

```
1. FastAPI cria a aplicação
2. Lifespan inicia (startup)
   ├─ Inicializa banco
   ├─ Inicializa queue
   └─ Inicializa worker
3. Servidor começa a aceitar requests
4. ... aplicação rodando ...
5. Servidor recebe sinal de parada
6. Lifespan finaliza (shutdown)
   ├─ Para worker
   └─ Fecha banco
7. Servidor fecha
```

## Routes (Endpoints)

### Definindo rotas

```python
# routes.py
from fastapi import APIRouter
from app.models import Task, TaskStatus, Priority
from app.services import create_task, get_task_by_id

router = APIRouter(prefix="/api/v1", tags=["tasks"])

@router.post("/tasks", status_code=201)
async def create_task_endpoint(req: CreateTaskRequest):
    """Cria uma nova task."""
    task = await create_task(name=req.name, payload=req.payload)
    return TaskResponse.from_task(task)

@router.get("/tasks")
async def list_tasks_endpoint(
    status: TaskStatus | None = None,
    limit: int = 50
):
    """Lista tasks."""
    tasks = await get_all_tasks(status=status, limit=limit)
    return [TaskResponse.from_task(t) for t in tasks]

@router.get("/tasks/{task_id}")
async def get_task_endpoint(task_id: uuid.UUID):
    """Busca task por ID."""
    task = await get_task_by_id(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return TaskResponse.from_task(task)
```

### Métodos HTTP

```python
@router.get("/items")      # GET — buscar
@router.post("/items")     # POST — criar
@router.put("/items/{id}") # PUT — atualizar
@router.delete("/items/{id}") # DELETE — remover
@router.patch("/items/{id}")  # PATCH — atualizar parcialmente
```

### Parâmetros

```python
# Path parameter
@router.get("/tasks/{task_id}")
async def get_task(task_id: uuid.UUID):
    ...

# Query parameter
@router.get("/tasks")
async def list_tasks(status: TaskStatus | None = None, limit: int = 50):
    ...

# Request body
@router.post("/tasks")
async def create_task(req: CreateTaskRequest):
    ...
```

## Request/Response Models

### Pydantic Models

```python
# routes.py
from pydantic import BaseModel, Field

class CreateTaskRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    payload: dict = Field(default_factory=dict)
    priority: Priority = Priority.MEDIUM

class TaskResponse(BaseModel):
    id: str
    name: str
    status: str
    priority: str
    created_at: str
    
    @classmethod
    def from_task(cls, task: Task) -> "TaskResponse":
        return cls(
            id=str(task.id),
            name=task.name,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at.isoformat(),
        )
```

### Validação Automática

```python
# Se enviar:
POST /api/v1/tasks
{
    "name": "",  # ❌ min_length=1
    "priority": "invalid"  # ❌ não é um Priority válido
}

# FastAPI retorna automaticamente:
HTTP 422 Unprocessable Entity
{
    "detail": [
        {
            "loc": ["body", "name"],
            "msg": "ensure this value has at least 1 characters",
            "type": "value_error.any_str.min_length"
        },
        {
            "loc": ["body", "priority"],
            "msg": "unexpected value; permitted: <Priority.LOW: 'low'>, ...",
            "type": "value_error.const"
        }
    ]
}
```

## Dependency Injection

### O que é?

Sistema para injetar dependências nos endpoints.

### Exemplo

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    """Retorna uma session do banco."""
    session = await get_session()
    async with session:
        yield session

@router.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)):
    """Usa a session injetada."""
    tasks = await list_tasks(db)
    return tasks
```

### Benefícios

- **Testável** — fácil mockar dependências
- **Reusável** — mesma lógica em múltiplos endpoints
- **Limpo** — separa concerns
- **Automático** — FastAPI gerencia o ciclo de vida

## Middleware

### O que é?

Código que roda antes/depois de cada request.

### Exemplo

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Middlewares Comuns

```python
# CORS
from fastapi.middleware.cors import CORSMiddleware

# GZip compression
from starlette.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# HTTPS redirect
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Exception Handling

### HTTP Exceptions

```python
from fastapi import HTTPException

@router.get("/tasks/{task_id}")
async def get_task(task_id: uuid.UUID):
    task = await get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    return task
```

### Custom Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class TaskNotFoundError(Exception):
    def __init__(self, task_id: str):
        self.task_id = task_id

@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Task {exc.task_id} not found"},
    )

@router.get("/tasks/{task_id}")
async def get_task(task_id: uuid.UUID):
    task = await get_task_by_id(task_id)
    if not task:
        raise TaskNotFoundError(str(task_id))
    return task
```

## Background Tasks

### O que é?

Tasks que rodam em background depois de retornar a response.

### Exemplo

```python
from fastapi import BackgroundTasks

async def send_email_notification(email: str, message: str):
    """Envia email em background."""
    await asyncio.sleep(2)  # Simula envio
    print(f"Email sent to {email}: {message}")

@router.post("/tasks")
async def create_task(
    req: CreateTaskRequest,
    background_tasks: BackgroundTasks
):
    task = await create_task(name=req.name, payload=req.payload)
    
    # Envia notificação em background
    background_tasks.add_task(
        send_email_notification,
        email="admin@example.com",
        message=f"New task created: {task.name}"
    )
    
    return task  # Retorna imediatamente, email enviado em background
```

## WebSocket

### Exemplo

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

## Documentação Automática

### Endpoints

```
GET /docs     — Swagger UI
GET /redoc    — ReDoc
GET /openapi.json — OpenAPI schema
```

### Customizando

```python
app = FastAPI(
    title="Async POC",
    description="POC com FastAPI + Granian + Queuefy",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

## Async/Await

### Tudo é async

```python
# ✅ Correto
@router.get("/tasks")
async def list_tasks():
    tasks = await get_all_tasks()  # async
    return tasks

# ❌ Errado (bloqueia o event loop)
@router.get("/tasks")
def list_tasks():  # sync — bloqueia!
    tasks = get_all_tasks()  # bloqueia
    return tasks
```

### Quando usar sync?

```python
# Use sync apenas para operações CPU-bound muito rápidas
@router.get("/calculate")
def calculate():
    result = sum(range(1000))  # rápido, não bloqueia
    return {"result": result}

# Para I/O (banco, API externa), sempre use async
@router.get("/tasks")
async def list_tasks():
    tasks = await get_all_tasks()  # I/O — async
    return tasks
```

## Testing

### Testando endpoints

```python
# tests/test_routes.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/tasks",
            json={"name": "test", "payload": {"foo": "bar"}}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test"
    assert data["status"] == "pending"
```

## Produção

### Configurações importantes

```python
app = FastAPI(
    title="Async POC",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,  # Desabilita em produção
    redoc_url="/redoc" if settings.debug else None,
)
```

### Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

### Rate Limiting

```python
# Use slowapi ou outro middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/tasks")
@limiter.limit("10/minute")
async def create_task(request: Request, req: CreateTaskRequest):
    ...
```

## Links

- [FastAPI no GitHub](https://github.com/tiangolo/fastapi)
- [Documentação Oficial](https://fastapi.tiangolo.com/)
- [Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic](https://docs.pydantic.dev/)
