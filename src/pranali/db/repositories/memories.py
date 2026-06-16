import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.pranali.db.models import MemoryItem
from pgvector.sqlalchemy import Vector

class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, memory: MemoryItem) -> MemoryItem:
        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def update(self, memory: MemoryItem) -> MemoryItem:
        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def update_many(self, memories: List[MemoryItem]) -> None:
        await self.session.commit()
        for m in memories:
            await self.session.refresh(m)

    async def get_recent_active_memories(self, user_id: uuid.UUID, limit: int = 10) -> List[MemoryItem]:
        result = await self.session.execute(
            select(MemoryItem)
            .where(MemoryItem.user_id == user_id, MemoryItem.active == True)
            .order_by(desc(MemoryItem.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_similar(self, user_id: uuid.UUID, embedding: List[float], limit: int = 5) -> List[MemoryItem]:
        # Using inner product or cosine distance. Here we use l2 distance for simplicity or cosine
        # The model uses `Vector(1536)`
        # `MemoryItem.embedding.cosine_distance(embedding)`
        result = await self.session.execute(
            select(MemoryItem)
            .where(MemoryItem.user_id == user_id, MemoryItem.active == True, MemoryItem.embedding.is_not(None))
            .order_by(MemoryItem.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_exact_match(self, user_id: uuid.UUID, memory_type: str, title: str) -> Optional[MemoryItem]:
        result = await self.session.execute(
            select(MemoryItem).where(
                MemoryItem.user_id == user_id,
                MemoryItem.memory_type == memory_type,
                MemoryItem.title == title,
                MemoryItem.active == True
            ).limit(1)
        )
        return result.scalars().first()

    async def get_similar_for_deduplication(self, user_id: uuid.UUID, memory_type: str, embedding: List[float], similarity_threshold: float = 0.85) -> Optional[MemoryItem]:
        # Uses cosine distance. 1 - cosine_distance = cosine_similarity
        result = await self.session.execute(
            select(MemoryItem).where(
                MemoryItem.user_id == user_id,
                MemoryItem.memory_type == memory_type,
                MemoryItem.active == True,
                MemoryItem.embedding.is_not(None),
                (1.0 - MemoryItem.embedding.cosine_distance(embedding)) > similarity_threshold
            ).order_by(MemoryItem.embedding.cosine_distance(embedding)).limit(1)
        )
        return result.scalars().first()
