# 🔮 Prefect — Orquestração de Workflows

## O que é?

Prefect é uma **plataforma de orquestração de workflows** moderna que permite definir, executar e monitorar pipelines de dados e tarefas complexas.

## Por que Prefect?

### Comparação com outras opções

| Ferramenta | Complexidade | UI | Retry | Scheduling |
|------------|--------------|----|-------|-----------|
| **Celery** | Alta | ❌ | ✅ | ✅ |
| **Airflow** | Alta | ✅ | ✅ | ✅ |
| **Prefect** | **Média** | **✅** | **✅** | **✅** |

### Vantagens

1. **Python First** — Decorators simples (@flow, @task)
2. **Dashboard visual** — UI moderna para monitoramento
3. **Retry automático** — Configuração flexível
4. **Scheduling** — Cron e intervalos
5. **Hybrid execution** — Cloud ou self-hosted
6. **Observabilidade** — Logs, métricas, tracing

## Instalação

```bash
# Com uv
uv add prefect

# Com pip
pip install prefect
```

## Conceitos Fundamentais

### Flow

Um **flow** é um workflow completo — uma sequência de tasks.

```python
from prefect import flow

@flow(name="data-pipeline")
async def data_pipeline(source: str = "api"):
    """Pipeline ETL completo."""
    raw = await fetch_data(source)
    transformed = await transform_data(raw)
    result = await save_results(transformed)
    return result
```

### Task

Uma **task** é uma unidade de trabalho dentro de um flow.

```python
from prefect import task

@task(retries=3, retry_delay_seconds=10)
async def fetch_data(source: str) -> dict:
    """Busca dados de uma fonte."""
    await asyncio.sleep(0.5)
    return {"source": source, "records": 100}
```

### Diferença Flow vs Task

```python
# Flow — orquestra tasks
@flow
async def my_flow():
    result1 = await task1()
    result2 = await task2(result1)
    return result2

# Task — executa trabalho
@task
async def task1():
    return {"data": "value"}
```

## Estrutura Básica

### Definindo flows

```python
# flows.py
import asyncio
from datetime import datetime
from prefect import flow, task, get_run_logger

@task(retries=3, retry_delay_seconds=10)
async def fetch_data(source: str) -> dict:
    """Busca dados (simulado)."""
    log = get_run_logger()
    log.info(f"Fetching from {source}")
    await asyncio.sleep(0.5)
    return {"source": source, "records": 100}

@task(retries=2)
async def transform_data(raw: dict) -> dict:
    """Transforma dados."""
    await asyncio.sleep(0.2)
    return {"transformed": True, "count": raw.get("records", 0)}

@task
async def save_results(data: dict) -> dict:
    """Salva resultados."""
    await asyncio.sleep(0.1)
    return {"saved": True, "count": data.get("count", 0)}

@flow(name="data-pipeline")
async def data_pipeline(source: str = "api") -> dict:
    """Pipeline ETL completo."""
    log = get_run_logger()
    log.info(f"Pipeline starting: {source}")
    
    raw = await fetch_data(source)
    transformed = await transform_data(raw)
    result = await save_results(transformed)
    
    log.info(f"Pipeline done: {result}")
    return result
```

### Tornando opcional

```python
# flows.py
try:
    from prefect import flow, task, get_run_logger
    PREFECT_OK = True
except ImportError:
    PREFECT_OK = False

if PREFECT_OK:
    @flow(name="data-pipeline")
    async def data_pipeline(source: str = "api") -> dict:
        ...
else:
    async def data_pipeline(source: str = "api") -> dict:
        return {"error": "Prefect not installed"}
```

## Executando Flows

### Direto do Python

```python
import asyncio
from app.flows import data_pipeline

async def main():
    result = await data_pipeline(source="api")
    print(result)

asyncio.run(main())
```

### Via API

```python
# routes.py
from app.flows import data_pipeline, PREFECT_OK

@router.post("/flows/pipeline")
async def run_pipeline(source: str = "api"):
    if not PREFECT_OK:
        raise HTTPException(503, "Prefect not available")
    return await data_pipeline(source)
```

### Via CLI

```bash
# Executar flow
prefect deployment run data-pipeline/my-deployment

# Ver status
prefect flow-run ls
```

## Retry e Error Handling

### Retry automático

```python
@task(retries=3, retry_delay_seconds=10)
async def unreliable_task():
    """Tenta 3 vezes com 10s entre tentativas."""
    if random.random() < 0.5:
        raise ValueError("Random failure")
    return "success"
```

### Retry com backoff

```python
from prefect.tasks import task

@task(
    retries=3,
    retry_delay_seconds=[5, 15, 45],  # Backoff exponencial
    retry_jitter_seconds=5  # Jitter aleatório
)
async def task_with_backoff():
    ...
```

### Error handling

```python
@task
async def task_that_might_fail():
    try:
        result = await do_something()
        return result
    except Exception as e:
        # Log error
        get_run_logger().error(f"Failed: {e}")
        raise  # Re-raise para trigger retry
```

## Scheduling

### Cron schedule

```python
from prefect.deployments import Deployment
from prefect.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=data_pipeline,
    schedule=CronSchedule(cron="0 4 * * *"),  # Todo dia às 4h
)
```

### Interval schedule

```python
from prefect.schedules import IntervalSchedule
from datetime import timedelta

deployment = Deployment.build_from_flow(
    flow=data_pipeline,
    schedule=IntervalSchedule(interval=timedelta(hours=1)),
)
```

### RRule schedule

```python
from prefect.schedules import RRuleSchedule

# Toda segunda-feira às 9h
deployment = Deployment.build_from_flow(
    flow=data_pipeline,
    schedule=RRuleSchedule(rrule="FREQ=WEEKLY;BYDAY=MO;BYHOUR=9"),
)
```

## Logging

### get_run_logger

```python
from prefect import get_run_logger

@task
async def my_task():
    log = get_run_logger()
    log.info("Starting task")
    log.warning("Something might be wrong")
    log.error("Something went wrong")
    return "done"
```

### Log levels

```python
log.debug("Debug message")
log.info("Info message")
log.warning("Warning message")
log.error("Error message")
log.critical("Critical message")
```

## Parameters

### Flow parameters

```python
@flow
async def my_flow(
    source: str = "api",
    batch_size: int = 100,
    dry_run: bool = False
):
    log = get_run_logger()
    log.info(f"Source: {source}, Batch: {batch_size}, Dry: {dry_run}")
```

### Task parameters

```python
@task
async def process_item(item_id: int, options: dict):
    ...
```

## State

### Task states

```python
from prefect.states import Completed, Failed

@task
async def my_task():
    try:
        result = await do_work()
        return Completed(message="Success", data=result)
    except Exception as e:
        return Failed(message=str(e))
```

### Flow states

```python
from prefect import flow
from prefect.states import Completed

@flow
async def my_flow():
    result = await task1()
    return Completed(data=result)
```

## Prefect Server

### Self-hosted

```bash
# Iniciar servidor
prefect server start

# Acessar UI
# http://localhost:4200
```

### Docker

```bash
docker run -p 4200:4200 prefecthq/prefect:3-python3.13
```

### Configuração

```bash
# Configurar API URL
prefect config set PREFECT_API_URL=http://localhost:4200/api

# Ver config
prefect config view
```

## Deployments

### Criando deployment

```python
from prefect.deployments import Deployment
from prefect.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=data_pipeline,
    name="daily-pipeline",
    schedule=CronSchedule(cron="0 4 * * *"),
    tags=["etl", "daily"],
)

deployment.apply()
```

### Via CLI

```bash
# Criar deployment
prefect deployment build flows.py:data_pipeline \
    --name "daily-pipeline" \
    --cron "0 4 * * *" \
    --tag etl

# Aplicar
prefect deployment apply data_pipeline-deployment.yaml
```

## Monitoring

### Dashboard

Acesse `http://localhost:4200` para ver:
- Flow runs
- Task runs
- Logs
- Métricas
- Schedules

### API

```bash
# Listar flow runs
curl http://localhost:4200/api/flow_runs

# Ver flow run específico
curl http://localhost:4200/api/flow_runs/{id}
```

## Integração com Queuefy

### Quando usar cada um?

| Caso | Usar |
|------|------|
| Task simples, rápida | **Queuefy** |
| Pipeline complexo, múltiplos steps | **Prefect** |
| Cron job simples | **Queuefy** |
| Workflow com dependências | **Prefect** |
| Retry básico | **Queuefy** |
| Retry avançado, backoff | **Prefect** |
| Monitoring visual | **Prefect** |

### Usando juntos

```python
# Queuefy enfileira, Prefect orquestra
@_queuefy.task("complex_pipeline")
async def handle_pipeline(task_id: str, config: dict):
    """Queuefy chama Prefect para orquestrar."""
    from app.flows import complex_flow
    
    # Prefect executa o workflow complexo
    result = await complex_flow(config)
    
    return result
```

## Exemplos Práticos

### ETL Pipeline

```python
@flow(name="etl-pipeline")
async def etl_pipeline(source: str, target: str):
    """Pipeline ETL completo."""
    log = get_run_logger()
    
    # Extract
    log.info(f"Extracting from {source}")
    raw_data = await extract(source)
    
    # Transform
    log.info("Transforming data")
    transformed = await transform(raw_data)
    
    # Load
    log.info(f"Loading to {target}")
    await load(transformed, target)
    
    log.info("ETL complete")
    return {"status": "success"}
```

### Batch Processing

```python
@flow(name="batch-process")
async def batch_process(items: list[str]):
    """Processa batch de items."""
    log = get_run_logger()
    
    results = []
    for item in items:
        result = await process_item(item)
        results.append(result)
    
    log.info(f"Processed {len(results)} items")
    return results
```

### Scheduled Report

```python
@flow(name="daily-report")
async def daily_report():
    """Gera relatório diário."""
    log = get_run_logger()
    
    # Coleta dados
    stats = await get_stats()
    
    # Gera relatório
    report = await generate_report(stats)
    
    # Envia por email
    await send_email(report)
    
    log.info("Daily report sent")
    return report
```

## Produção

### Prefect Cloud

```bash
# Login
prefect cloud login

# Deploy
prefect deployment apply deployment.yaml
```

### Self-hosted

```bash
# Docker Compose
version: '3'
services:
  prefect:
    image: prefecthq/prefect:3-python3.13
    ports:
      - "4200:4200"
    environment:
      - PREFECT_SERVER_API_HOST=0.0.0.0
```

### High Availability

```bash
# Múltiplos workers
prefect worker start --pool my-pool --limit 4

# Kubernetes
kubectl apply -f prefect-worker.yaml
```

## Links

- [Prefect no GitHub](https://github.com/PrefectHQ/prefect)
- [Documentação Oficial](https://docs.prefect.io/)
- [Prefect Cloud](https://app.prefect.cloud/)
- [Exemplos](https://docs.prefect.io/latest/examples/)
