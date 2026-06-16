from sqlalchemy import text
from src.pranali.db.session import get_engine

async def check_db_health() -> bool:
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

async def check_pgvector_health() -> bool:
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            ext = result.scalars().first()
            return bool(ext)
    except Exception:
        return False
