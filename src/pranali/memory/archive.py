import uuid
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.repositories.memories import MemoryRepository

logger = structlog.get_logger(__name__)

class MemoryArchive:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = MemoryRepository(session)

    async def archive_stale_memories(self, user_id: uuid.UUID) -> int:
        memories = await self.repository.get_recent_active_memories(user_id, limit=1000)

        to_update = []
        for m in memories:
            # Simple archive logic: low importance and very low recency
            if m.importance_score < 0.4 and m.recency_score <= 0.2:
                m.active = False
                m.archived = True
                to_update.append(m)

        if to_update:
            await self.repository.update_many(to_update)
            logger.info("memory_archive_completed", count=len(to_update))

        return len(to_update)
