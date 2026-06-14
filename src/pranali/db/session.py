from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.pranali.config import settings

# Create global async engine
engine = create_async_engine(
    settings.database.url,
    echo=False,
    future=True,
    pool_pre_ping=True
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session():
    """Dependency to provide a database session."""
    async with AsyncSessionFactory() as session:
        yield session
