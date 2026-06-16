import structlog
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.repositories.memories import MemoryRepository
from src.pranali.db.models import MemoryItem
from src.pranali.memory.schemas import MemoryCreate

logger = structlog.get_logger(__name__)

class MemoryWriter:
    def __init__(self, session: AsyncSession):
        self.repository = MemoryRepository(session)

    async def write(self, candidate: MemoryCreate, embedding: Optional[list[float]] = None, embedding_model: Optional[str] = None) -> MemoryItem:
        existing = None

        # For Phase 2, the decision engine in extractor should dictate if this is CREATE or UPDATE,
        # but as a fallback safety layer, we maintain the deduplication check here.

        existing = await self.repository.get_by_exact_match(candidate.user_id, candidate.memory_type, candidate.title)
        if not existing and embedding:
            existing = await self.repository.get_similar_for_deduplication(candidate.user_id, candidate.memory_type, embedding)

        if existing:
            existing.version += 1
            existing.content = candidate.content
            existing.summary = candidate.summary
            existing.importance_score = max(existing.importance_score, candidate.importance_score)
            existing.confidence_score = min(1.0, existing.confidence_score + 0.1)
            existing.confirmed = candidate.confirmed
            if embedding:
                existing.embedding = embedding
                existing.embedding_model = embedding_model
            logger.info("memory_updated", id=str(existing.id), version=existing.version)
            return await self.repository.update(existing)
        else:
            # Create new
            new_item = MemoryItem(
                user_id=candidate.user_id,
                memory_type=candidate.memory_type,
                title=candidate.title,
                content=candidate.content,
                summary=candidate.summary,
                entities=candidate.entities,
                tags=candidate.tags,
                embedding=embedding,
                embedding_model=embedding_model,
                importance_score=candidate.importance_score,
                confidence_score=candidate.confidence_score,
                emotional_weight=candidate.emotional_weight,
                sensitive=candidate.sensitive,
                confirmed=candidate.confirmed,
                source=candidate.source,
                source_event_id=candidate.source_event_id
            )
            created = await self.repository.create(new_item)
            logger.info("memory_created", id=str(created.id), type=created.memory_type)
            return created
