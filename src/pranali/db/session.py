from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.pranali.config import settings

_engine = None
_AsyncSessionFactory = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database.url,
            echo=False,
            future=True,
            pool_pre_ping=True
        )
    return _engine

def get_session_factory():
    global _AsyncSessionFactory
    if _AsyncSessionFactory is None:
        _AsyncSessionFactory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
    return _AsyncSessionFactory

async def get_db_session():
    """Dependency to provide a database session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session
