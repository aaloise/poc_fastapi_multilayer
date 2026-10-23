# 🧪 Testing — Guia de Testes

## Visão Geral

Este guia cobre como testar a aplicação em diferentes níveis.

## Tipos de Testes

| Tipo | Velocidade | Cobertura | Quando usar |
|------|------------|-----------|-------------|
| **Unit** | Rápido | Baixa | Lógica isolada |
| **Integration** | Médio | Média | Componentes juntos |
| **E2E** | Lento | Alta | Fluxo completo |

## Instalação

```bash
# Com uv
uv add --dev pytest pytest-asyncio

# Com pip
pip install pytest pytest-asyncio
```

## Configuração

### pyproject.toml

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Testes Unitários

### Testando Models

```python
# tests/test_models.py
import pytest
from app.models import Task, TaskStatus, Priority

class TestTask:
    """Testes do modelo Task."""
    
    def test_create_task(self):
        """Testa criação de task."""
        task = Task(name="test", payload={"key": "value"})
        
        assert task.name == "test"
        assert task.payload == {"key": "value"}
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.MEDIUM
        assert task.attempts == 0
    
    def test_task_with_priority(self):
        """Testa task com prioridade."""
        task = Task(name="urgent", priority=Priority.HIGH)
        assert task.priority == Priority.HIGH
    
    def test_task_status_values(self):
        """Testa valores de status."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
    
    def test_task_priority_values(self):
        """Testa valores de prioridade."""
        assert Priority.LOW == "low"
        assert Priority.MEDIUM == "medium"
        assert Priority.HIGH == "high"
        assert Priority.CRITICAL == "critical"
```

### Testando Config

```python
# tests/test_config.py
import pytest
from app.config import Settings

class TestSettings:
    """Testes de configuração."""
    
    def test_default_settings(self):
        """Testa valores padrão."""
        settings = Settings()
        
        assert settings.app_name == "Async POC"
        assert settings.debug is False
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.queue_concurrency == 8
    
    def test_override_via_env(self, monkeypatch):
        """Testa override via variáveis de ambiente."""
        monkeypatch.setenv("POC_PORT", "9000")
        monkeypatch.setenv("POC_DEBUG", "true")
        
        settings = Settings()
        
        assert settings.port == 9000
        assert settings.debug is True
    
    def test_db_url(self, monkeypatch):
        """Testa URL do banco."""
        monkeypatch.setenv("POC_DB_URL", "postgresql+asyncpg://localhost/test")
        
        settings = Settings()
        
        assert settings.db_url == "postgresql+asyncpg://localhost/test"
```

## Testes de Integração

### Testando Services

```python
# tests/test_services.py
import pytest
import uuid
from unittest.mock import AsyncMock, patch
from app.models import Task, TaskStatus
from app.services import create_task, execute_task, get_task_by_id

class TestCreateTask:
    """Testes de create_task."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self):
        """Testa criação bem-sucedida."""
        with patch("app.services.get_session") as mock_get_session:
            # Mock session
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            mock_session.__aenter__.return_value = mock_session
            
            # Mock save_task
            with patch("app.services.save_task") as mock_save:
                mock_save.return_value = Task(
                    id=uuid.uuid4(),
                    name="test",
                    status=TaskStatus.PENDING
                )
                
                # Mock enqueue
                with patch("app.services.enqueue") as mock_enqueue:
                    task = await create_task(name="test", payload={"foo": "bar"})
                    
                    assert task.name == "test"
                    assert task.status == TaskStatus.PENDING
                    mock_save.assert_called_once()
                    mock_enqueue.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_task_with_priority(self):
        """Testa criação com prioridade."""
        from app.models import Priority
        
        with patch("app.services.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            mock_session.__aenter__.return_value = mock_session
            
            with patch("app.services.save_task") as mock_save:
                mock_save.return_value = Task(
                    id=uuid.uuid4(),
                    name="urgent",
                    priority=Priority.HIGH
                )
                
                with patch("app.services.enqueue"):
                    task = await create_task(
                        name="urgent",
                        priority=Priority.HIGH
                    )
                    
                    assert task.priority == Priority.HIGH

class TestExecuteTask:
    """Testes de execute_task."""
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Testa execução bem-sucedida."""
        task_id = uuid.uuid4()
        
        with patch("app.services.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            mock_session.__aenter__.return_value = mock_session
            
            # Mock get_task
            with patch("app.services.get_task") as mock_get:
                mock_get.return_value = Task(
                    id=task_id,
                    name="test",
                    status=TaskStatus.PENDING
                )
                
                # Mock save_task
                with patch("app.services.save_task") as mock_save:
                    result = await execute_task(task_id)
                    
                    assert result["success"] is True
                    assert result["task_id"] == str(task_id)
                    assert mock_save.call_count == 2  # running + completed
    
    @pytest.mark.asyncio
    async def test_execute_task_not_found(self):
        """Testa execução de task inexistente."""
        task_id = uuid.uuid4()
        
        with patch("app.services.get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            mock_session.__aenter__.return_value = mock_session
            
            with patch("app.services.get_task") as mock_get:
                mock_get.return_value = None
                
                result = await execute_task(task_id)
                
                assert result["success"] is False
                assert "not found" in result["error"].lower()
```

### Testando Database

```python
# tests/test_database.py
import pytest
from app.database import init_db, get_session, close_db
from app.models import Task, save_task, get_task

class TestDatabase:
    """Testes de banco de dados."""
    
    @pytest.fixture(autouse=True)
    async def setup_db(self):
        """Inicializa banco em memória."""
        await init_db("sqlite+aiosqlite:///:memory:")
        yield
        await close_db()
    
    @pytest.mark.asyncio
    async def test_save_and_get_task(self):
        """Testa salvar e buscar task."""
        task = Task(name="test", payload={"foo": "bar"})
        
        # Save
        session = await get_session()
        async with session:
            saved = await save_task(session, task)
        
        assert saved.id == task.id
        assert saved.name == "test"
        
        # Get
        session = await get_session()
        async with session:
            fetched = await get_task(session, task.id)
        
        assert fetched is not None
        assert fetched.id == task.id
        assert fetched.name == "test"
    
    @pytest.mark.asyncio
    async def test_update_task(self):
        """Testa atualizar task."""
        task = Task(name="test", status="pending")
        
        # Save
        session = await get_session()
        async with session:
            saved = await save_task(session, task)
        
        # Update
        saved.status = "running"
        session = await get_session()
        async with session:
            updated = await save_task(session, saved)
        
        assert updated.status == "running"
        
        # Verify
        session = await get_session()
        async with session:
            fetched = await get_task(session, task.id)
        
        assert fetched.status == "running"
```

## Testes de API (E2E)

### Testando Routes

```python
# tests/test_routes.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestTaskAPI:
    """Testes da API de tasks."""
    
    @pytest.mark.asyncio
    async def test_create_task(self):
        """Testa criar task via API."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tasks",
                json={
                    "name": "test_task",
                    "payload": {"foo": "bar"},
                    "priority": "medium"
                }
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_task"
        assert data["status"] == "pending"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_task_validation_error(self):
        """Testa validação de request."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tasks",
                json={
                    "name": "",  # vazio — deve falhar
                    "priority": "invalid"  # inválido
                }
            )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_list_tasks(self):
        """Testa listar tasks."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create some tasks
            await client.post("/api/v1/tasks", json={"name": "task1"})
            await client.post("/api/v1/tasks", json={"name": "task2"})
            
            # List
            response = await client.get("/api/v1/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    @pytest.mark.asyncio
    async def test_get_task(self):
        """Testa buscar task por ID."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create
            create_resp = await client.post(
                "/api/v1/tasks",
                json={"name": "test"}
            )
            task_id = create_resp.json()["id"]
            
            # Get
            response = await client.get(f"/api/v1/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["name"] == "test"
    
    @pytest.mark.asyncio
    async def test_get_task_not_found(self):
        """Testa buscar task inexistente."""
        import uuid
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/api/v1/tasks/{uuid.uuid4()}")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Testa obter estatísticas."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/tasks/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pending" in data
        assert "running" in data
        assert "completed" in data
        assert "failed" in data
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Testa health check."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "components" in data
```

## Fixtures

### Fixtures comuns

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from app.models import Task, TaskStatus
from app.database import init_db, close_db

@pytest.fixture(autouse=True)
async def setup_test_db():
    """Inicializa banco em memória para cada teste."""
    await init_db("sqlite+aiosqlite:///:memory:")
    yield
    await close_db()

@pytest.fixture
def sample_task():
    """Task de exemplo."""
    return Task(
        name="test_task",
        payload={"foo": "bar"},
        status=TaskStatus.PENDING
    )

@pytest.fixture
def mock_session():
    """Session mock."""
    session = AsyncMock()
    session.__aenter__.return_value = session
    return session
```

## Executando Testes

### Comandos

```bash
# Todos os testes
uv run pytest

# Verbose
uv run pytest -v

# Com coverage
uv run pytest --cov=src/app --cov-report=term-missing

# Apenas um arquivo
uv run pytest tests/test_models.py

# Apenas uma classe
uv run pytest tests/test_services.py::TestCreateTask

# Apenas um teste
uv run pytest tests/test_services.py::TestCreateTask::test_create_task_success

# Parar no primeiro erro
uv run pytest -x

# Mostrar output
uv run pytest -s
```

### Makefile

```makefile
test:
	uv run pytest tests/ -v --asyncio-mode=auto

test-cov:
	uv run pytest tests/ -v --asyncio-mode=auto \
		--cov=src/app --cov-report=term-missing

test-watch:
	uv run ptw
```

## Coverage

### Configuração

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src/app"]
omit = ["tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

### Relatório

```bash
# Terminal
uv run pytest --cov=src/app --cov-report=term-missing

# HTML
uv run pytest --cov=src/app --cov-report=html
# Abra htmlcov/index.html

# XML (para CI)
uv run pytest --cov=src/app --cov-report=xml
```

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    
    - name: Install dependencies
      run: uv sync --dev
    
    - name: Run tests
      run: uv run pytest tests/ -v --cov=src/app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Boas Práticas

### 1. Testes independentes

```python
# ✅ Correto — cada teste é independente
def test_create_task():
    task = Task(name="test")
    assert task.name == "test"

def test_another_task():
    task = Task(name="another")
    assert task.name == "another"

# ❌ Errado — testes dependem um do outro
task = None

def test_create_task():
    global task
    task = Task(name="test")
    assert task is not None

def test_use_task():
    assert task.name == "test"  # depende do teste anterior!
```

### 2. Nomes descritivos

```python
# ✅ Correto — nome descreve o comportamento
def test_create_task_with_high_priority():
    task = Task(name="urgent", priority=Priority.HIGH)
    assert task.priority == Priority.HIGH

# ❌ Errado — nome genérico
def test_task():
    task = Task(name="urgent", priority=Priority.HIGH)
    assert task.priority == Priority.HIGH
```

### 3. Arrange-Act-Assert

```python
# ✅ Correto — padrão AAA
def test_execute_task():
    # Arrange
    task = Task(name="test", status=TaskStatus.PENDING)
    
    # Act
    result = await execute_task(task.id)
    
    # Assert
    assert result["success"] is True
```

### 4. Mock apenas o necessário

```python
# ✅ Correto — mocka apenas dependências externas
async def test_create_task():
    with patch("app.services.enqueue") as mock_enqueue:
        task = await create_task(name="test")
        mock_enqueue.assert_called_once()

# ❌ Errado — mocka tudo
async def test_create_task():
    with patch("app.services.Task") as mock_task:
        with patch("app.services.save_task") as mock_save:
            with patch("app.services.enqueue") as mock_enqueue:
                # Teste frágil — testa mocks, não lógica
```

### 5. Teste erros

```python
# ✅ Correto — testa cenários de erro
async def test_execute_task_not_found():
    result = await execute_task(uuid.uuid4())
    assert result["success"] is False
    assert "not found" in result["error"].lower()

# ❌ Errado — testa apenas happy path
async def test_execute_task():
    result = await execute_task(task_id)
    assert result["success"] is True
```

## Debugging

### Ver output

```bash
# Print statements
uv run pytest -s

# Logs
uv run pytest --log-cli-level=DEBUG
```

### Breakpoints

```python
def test_something():
    import pdb; pdb.set_trace()
    # ou
    breakpoint()
    
    task = Task(name="test")
    assert task.name == "test"
```

### Ver exceções

```bash
# Mostrar traceback completo
uv run pytest --tb=long

# Mostrar apenas primeira linha
uv run pytest --tb=line
```

## Links

- [pytest Docs](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Mock Guide](https://docs.python.org/3/library/unittest.mock.html)
