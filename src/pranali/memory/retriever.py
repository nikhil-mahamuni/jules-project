import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.repositories.memories import MemoryRepository
from src.pranali.memory.schemas import RetrievedMemory
from src.pranali.memory.scorer import calculate_final_score

class MemoryRetriever:
    def __init__(self, session: AsyncSession):
        self.repository = MemoryRepository(session)

    async def retrieve(self, user_id: uuid.UUID, top_k: int = 8, embedding: Optional[List[float]] = None) -> List[RetrievedMemory]:
        import asyncio

        # Phase 2: Multi-channel concurrent retrieval
        tasks = []

        if embedding:
            tasks.append(self.repository.search_similar(user_id, embedding, limit=top_k))
        else:
            async def empty_list(): return []
            tasks.append(empty_list())

        tasks.append(self.repository.get_recent_active_memories(user_id, limit=top_k))

        results = await asyncio.gather(*tasks)

        memories = []
        for res in results:
            memories.extend(res)

        # Deduplicate
        unique_memories = {}
        for m in memories:
            unique_memories[m.id] = m

        # 4. Rank with scorer
        scored_memories = []
        for m in unique_memories.values():
            # Mock similarity if vector wasn't used or isn't available
            similarity = 0.5
            score = calculate_final_score(
                similarity=similarity,
                importance=m.importance_score,
                confidence=m.confidence_score,
                recency=m.recency_score,
                emotional_weight=m.emotional_weight
            )
            scored_memories.append(RetrievedMemory(
                id=m.id,
                memory_type=m.memory_type,
                title=m.title,
                content=m.content,
                importance_score=m.importance_score,
                recency_score=m.recency_score,
                final_score=score,
                created_at=m.created_at
            ))

        # Sort by final_score descending
        scored_memories.sort(key=lambda x: x.final_score, reverse=True)
        top_memories = scored_memories[:top_k]

        # 5. Update retrieval_count and last_accessed_at for returned memories
        from src.pranali.utils.time import now
        current_time = now()

        to_update = []
        for top_m in top_memories:
            db_memory = unique_memories[top_m.id]
            db_memory.retrieval_count += 1
            db_memory.last_accessed_at = current_time
            to_update.append(db_memory)

        if to_update:
            await self.repository.update_many(to_update)

        return top_memories
