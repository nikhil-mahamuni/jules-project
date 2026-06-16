import uuid
import structlog
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.repositories.memories import MemoryRepository
from src.pranali.db.models import MemoryItem

logger = structlog.get_logger(__name__)

class MemoryConsolidator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = MemoryRepository(session)

    async def consolidate_duplicates(self, user_id: uuid.UUID) -> int:
        """Finds active memories of the same type with high similarity and merges them."""
        # A simple naive consolidation for Phase 2:
        # Group by title and memory_type to find exact logical duplicates and merge versions.
        # In a full system, this would cluster by embeddings.

        all_active = await self.repository.get_recent_active_memories(user_id, limit=1000)

        grouped = {}
        for m in all_active:
            key = (m.memory_type, m.title)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(m)

        merged_count = 0
        to_update = []

        for key, memories in grouped.items():
            if len(memories) > 1:
                # Sort by newest first
                memories.sort(key=lambda x: x.created_at, reverse=True)
                primary = memories[0]

                # Archive the rest
                for duplicate in memories[1:]:
                    duplicate.active = False
                    duplicate.archived = True
                    primary.version += 1
                    primary.confidence_score = min(1.0, primary.confidence_score + 0.1)
                    to_update.append(duplicate)
                to_update.append(primary)
                merged_count += len(memories) - 1

        if to_update:
            await self.repository.update_many(to_update)
            logger.info("memory_consolidated", count=merged_count)

        return merged_count
