"""Setup do banco de dados — engine e session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base

# Engine global (inicializado no startup)
_engine = None
_session_factory = None


async def init_db(url: str) -> None:
    """Inicializa o banco: cria engine + tabelas."""
    global _engine, _session_factory

    _engine = create_async_engine(url, echo=False)
    _session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Retorna uma session nova."""
    if not _session_factory:
        raise RuntimeError("Banco não inicializado")
    return _session_factory()


async def close_db() -> None:
    """Fecha o engine."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
