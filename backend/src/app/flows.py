"""Prefect Flows — orquestração de workflows (opcional)."""

import asyncio
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger()

# Prefect é opcional
try:
    from prefect import flow, task, get_run_logger
    PREFECT_OK = True
except ImportError:
    PREFECT_OK = False
    logger.warning("prefect.not_installed")


if PREFECT_OK:
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

    @flow(name="batch-process")
    async def batch_process(size: int = 10) -> dict:
        """Processa batch de tasks."""
        log = get_run_logger()
        log.info(f"Processing batch: {size}")

        results = []
        for i in range(size):
            r = await fetch_data(f"item-{i}")
            results.append(r)

        return {"processed": len(results), "at": datetime.now(timezone.utc).isoformat()}

else:
    # Stubs quando Prefect não está instalado
    async def data_pipeline(source: str = "api") -> dict:
        return {"error": "Prefect not installed"}

    async def batch_process(size: int = 10) -> dict:
        return {"error": "Prefect not installed"}
