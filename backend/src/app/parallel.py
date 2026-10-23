"""
Processamento Paralelo com Joblib
==================================

Joblib é usado para processamento CPU-bound em paralelo.
Enquanto Queuefy gerencia tasks I/O-bound (async),
Joblib gerencia tasks CPU-bound (paralelas).

Quando usar cada um:
- Queuefy: I/O-bound (API calls, DB queries, file I/O)
- Joblib: CPU-bound (cálculos pesados, ML, data processing)
- Prefect: Orquestração de workflows complexos
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable

import structlog
from joblib import Parallel, delayed

logger = structlog.get_logger()


# Executor global para processamento paralelo
_executor: ProcessPoolExecutor | None = None


def init_parallel(n_jobs: int = -1) -> None:
    """
    Inicializa o executor de processamento paralelo.
    
    Args:
        n_jobs: Número de jobs paralelos. -1 usa todos os cores.
    """
    global _executor
    _executor = ProcessPoolExecutor(max_workers=n_jobs if n_jobs > 0 else None)
    logger.info("joblib.initialized", n_jobs=n_jobs)


def shutdown_parallel() -> None:
    """Finaliza o executor de processamento paralelo."""
    global _executor
    if _executor:
        _executor.shutdown(wait=True)
        _executor = None
        logger.info("joblib.shutdown")


async def parallel_map(
    func: Callable,
    items: list[Any],
    n_jobs: int = -1,
    **kwargs
) -> list[Any]:
    """
    Executa uma função em paralelo para uma lista de itens.
    
    Args:
        func: Função a ser executada (deve ser CPU-bound)
        items: Lista de itens para processar
        n_jobs: Número de jobs paralelos (-1 = todos os cores)
        **kwargs: Argumentos adicionais para a função
    
    Returns:
        Lista de resultados
    
    Exemplo:
        # Processar 1000 cálculos em paralelo
        results = await parallel_map(
            heavy_computation,
            range(1000),
            n_jobs=4
        )
    """
    loop = asyncio.get_event_loop()
    
    # Executa processamento paralelo em thread pool
    results = await loop.run_in_executor(
        _executor,
        lambda: Parallel(n_jobs=n_jobs, **kwargs)(
            delayed(func)(item) for item in items
        )
    )
    
    logger.info("joblib.parallel_map.completed", items=len(items), results=len(results))
    return results


async def parallel_batch(
    func: Callable,
    batches: list[list[Any]],
    n_jobs: int = -1,
    **kwargs
) -> list[list[Any]]:
    """
    Executa uma função em paralelo para lotes de itens.
    
    Args:
        func: Função a ser executada
        batches: Lista de lotes para processar
        n_jobs: Número de jobs paralelos
        **kwargs: Argumentos adicionais
    
    Returns:
        Lista de listas de resultados
    
    Exemplo:
        # Processar lotes de dados em paralelo
        results = await parallel_batch(
            process_batch,
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            n_jobs=3
        )
    """
    loop = asyncio.get_event_loop()
    
    results = await loop.run_in_executor(
        _executor,
        lambda: Parallel(n_jobs=n_jobs, **kwargs)(
            delayed(func)(batch) for batch in batches
        )
    )
    
    logger.info("joblib.parallel_batch.completed", batches=len(batches))
    return results


# ── Exemplos de Funções CPU-bound ────────────────────────────────────

def heavy_computation(n: int) -> int:
    """
    Exemplo de computação pesada (CPU-bound).
    
    Esta função simula um cálculo intensivo que se beneficia
    de processamento paralelo.
    """
    # Simula cálculo pesado
    result = 0
    for i in range(n * 1000):
        result += i * i
    return result


def process_data_batch(data: list[dict]) -> list[dict]:
    """
    Processa um lote de dados (CPU-bound).
    
    Exemplo: transformação de dados, feature engineering, etc.
    """
    results = []
    for item in data:
        # Simula processamento pesado
        processed = {
            **item,
            "processed": True,
            "hash": hash(str(item)) % 1000000,
        }
        results.append(processed)
    return results


def train_model_chunk(chunk: list[dict]) -> dict:
    """
    Treina um modelo em um chunk de dados (CPU-bound).
    
    Exemplo: treinamento distribuído de ML.
    """
    # Simula treinamento de modelo
    import time
    time.sleep(0.1)  # Simula treinamento
    
    return {
        "chunk_size": len(chunk),
        "accuracy": 0.95,
        "trained": True,
    }
