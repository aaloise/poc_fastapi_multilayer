"""
Queuefy — Fila de tarefas async
================================

Queuefy é uma task queue que usa o próprio banco de dados (SQLite/PostgreSQL)
para armazenar as tasks. Não precisa de Redis, RabbitMQ ou outro broker.

Como funciona:
1. Você registra handlers com @queuefy.task("nome")
2. Quando alguém chama enqueue("nome"), o Queuefy insere uma linha no banco
3. O Worker fica rodando em background, buscando tasks pendentes no banco
4. Quando encontra uma task, executa o handler correspondente
5. Marca como completed ou failed no banco

Vantagens:
- Zero dependências externas (usa o mesmo banco da aplicação)
- 100% async
- Suporta retry automático
- Suporta cron jobs (tasks agendadas)
- Multi-worker safe (vários workers podem rodar em paralelo)
"""

import uuid
import asyncio

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine
from queuefy.app import Queuefy
from queuefy.store.sqlalchemy import SqlAlchemyStore
from queuefy.worker import Worker

logger = structlog.get_logger()

# Instância global do Queuefy
_queuefy: Queuefy | None = None
_worker: Worker | None = None


async def init_queue(engine: AsyncEngine, concurrency: int = 8) -> None:
    """
    Inicializa o Queuefy.
    
    Args:
        engine: SQLAlchemy async engine (o mesmo banco da aplicação)
        concurrency: Quantas tasks podem rodar em paralelo
    """
    global _queuefy, _worker
    
    # Cria o Queuefy usando o banco de dados
    # O Queuefy vai criar suas próprias tabelas no mesmo banco
    store = SqlAlchemyStore(engine)
    _queuefy = Queuefy(store)
    
    # Cria as tabelas do Queuefy no banco
    await _queuefy.setup()
    
    # Registra os handlers (funções que processam as tasks)
    _register_handlers()
    
    # Inicia o worker em background
    _worker = Worker(_queuefy, concurrency=concurrency)
    asyncio.create_task(_worker.run())
    
    await logger.ainfo("queuefy.started", concurrency=concurrency)


def _register_handlers() -> None:
    """
    Registra os handlers de task.
    
    Cada handler é uma função async que será executada quando
    uma task com o nome correspondente for enfileirada.
    """
    if not _queuefy:
        return
    
    # Handler 1: Processar task genérica
    @_queuefy.task("process_task", max_attempts=3, timeout=60)
    async def handle_process_task(task_id: str, payload: dict) -> dict:
        """
        Handler para tasks genéricas.
        
        Quando alguém chama:
            await enqueue("process_task", task_id="123", payload={"foo": "bar"})
        
        O Queuefy vai:
        1. Inserir uma linha na tabela queuefy_runs
        2. O worker pega essa linha
        3. Executa esta função
        4. Marca como completed no banco
        """
        from app.services import execute_task
        
        await logger.ainfo("queuefy.handler.process_task", task_id=task_id)
        result = await execute_task(uuid.UUID(task_id))
        return result
    
    # Handler 2: Enviar notificação
    @_queuefy.task("send_notification", max_attempts=5, timeout=30)
    async def handle_send_notification(task_id: str, message: str, channel: str) -> dict:
        """
        Handler para notificações.
        
        Uso:
            await enqueue("send_notification", 
                         task_id="456",
                         message="Hello!",
                         channel="email")
        """
        await logger.ainfo("queuefy.handler.send_notification", 
                          task_id=task_id, 
                          channel=channel)
        
        # Simula envio de notificação
        await asyncio.sleep(0.05)
        
        return {"sent": True, "channel": channel, "message": message}
    
    # Handler 3: Relatório diário (cron job)
    @_queuefy.task("daily_report", cron="0 4 * * *")
    async def handle_daily_report() -> dict:
        """
        Task agendada com cron.
        
        Esta task roda automaticamente todos os dias às 4h da manhã.
        O Queuefy cria as "runs" automaticamente baseado no cron.
        """
        from app.services import get_stats
        
        await logger.ainfo("queuefy.handler.daily_report")
        stats = await get_stats()
        
        return {"report": stats, "generated_at": "now"}
    
    # Handler 4: Limpeza (cron job semanal)
    @_queuefy.task("weekly_cleanup", cron="0 2 * * 0")
    async def handle_weekly_cleanup() -> dict:
        """
        Limpeza semanal - roda todo domingo às 2h.
        """
        await logger.ainfo("queuefy.handler.weekly_cleanup")
        await asyncio.sleep(0.1)
        return {"cleaned": True}


async def enqueue(task_name: str, task_id: str | None = None, **kwargs) -> str:
    """
    Enfileira uma task para processamento async.
    
    Args:
        task_name: Nome do handler registrado (ex: "process_task")
        task_id: ID opcional (gera UUID se não fornecido)
        **kwargs: Argumentos passados para o handler
    
    Returns:
        task_id: ID da task enfileirada
    
    Exemplo:
        # Enfileira uma task genérica
        await enqueue("process_task", task_id="123", payload={"foo": "bar"})
        
        # Enfileira uma notificação
        await enqueue("send_notification", 
                     message="Hello!", 
                     channel="email")
    
    O que acontece internamente:
    1. Queuefy insere uma linha na tabela queuefy_runs
    2. A linha tem: task_name, task_id, kwargs, status=pending
    3. O worker (rodando em background) busca essa linha
    4. Executa o handler correspondente
    5. Atualiza o status para completed/failed
    """
    if not _queuefy:
        raise RuntimeError("Queuefy não inicializado. Chame init_queue() primeiro.")
    
    tid = task_id or str(uuid.uuid4())
    
    # Enfileira a task (insere no banco)
    await _queuefy.enqueue(task_name, task_id=tid, **kwargs)
    
    await logger.ainfo("queuefy.enqueued", task_name=task_name, task_id=tid)
    return tid


async def enqueue_at(task_name: str, when, **kwargs) -> str:
    """
    Agenda uma task para rodar em um horário específico.
    
    Args:
        task_name: Nome do handler
        when: datetime quando a task deve rodar
        **kwargs: Argumentos para o handler
    
    Exemplo:
        from datetime import datetime, timedelta
        
        # Rodar daqui a 1 hora
        await enqueue_at("process_task", 
                        when=datetime.utcnow() + timedelta(hours=1),
                        task_id="789",
                        payload={"scheduled": True})
    """
    if not _queuefy:
        raise RuntimeError("Queuefy não inicializado")
    
    tid = str(uuid.uuid4())
    await _queuefy.enqueue_at(task_name, when, **kwargs)
    
    await logger.ainfo("queuefy.scheduled", task_name=task_name, when=str(when))
    return tid


async def stop_queue() -> None:
    """Para o worker do Queuefy."""
    global _worker
    if _worker:
        await logger.ainfo("queuefy.stopping")
        # O worker vai parar quando a task atual terminar
        _worker = None
        await logger.ainfo("queuefy.stopped")


def get_queuefy() -> Queuefy | None:
    """Retorna a instância do Queuefy (para debug/monitoramento)."""
    return _queuefy
