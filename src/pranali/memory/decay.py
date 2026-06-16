import uuid
import structlog
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.repositories.memories import MemoryRepository
from src.pranali.utils.time import now

logger = structlog.get_logger(__name__)

class MemoryDecay:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = MemoryRepository(session)

    async def decay_memories(self, user_id: uuid.UUID) -> int:
        memories = await self.repository.get_recent_active_memories(user_id, limit=1000)
        current_time = now()

        to_update = []
        for m in memories:
            days_old = (current_time - m.updated_at).days
            if days_old > 0:
                # Apply decay based on type and importance
                decay_factor = 0.01
                if m.memory_type == "preference" and m.confirmed:
                    decay_factor = 0.001
                elif m.memory_type == "episodic" and m.importance_score < 0.5:
                    decay_factor = 0.05

                new_recency = max(0.1, m.recency_score - (days_old * decay_factor))
                if new_recency != m.recency_score:
                    m.recency_score = new_recency
                    to_update.append(m)

        if to_update:
            await self.repository.update_many(to_update)
            logger.info("memory_decay_completed", count=len(to_update))

        return len(to_update)
