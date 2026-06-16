import uuid
import structlog
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.repositories.memories import MemoryRepository
from src.pranali.db.models import MemoryItem
from src.pranali.llm.router import LLMRouter, LLMRole
from src.pranali.memory.schemas import MemoryCreate
from src.pranali.memory.writer import MemoryWriter

logger = structlog.get_logger(__name__)

class MemoryReflection:
    def __init__(self, session: AsyncSession, router: LLMRouter):
        self.session = session
        self.router = router
        self.repository = MemoryRepository(session)
        self.writer = MemoryWriter(session)

    async def reflect(self, user_id: uuid.UUID) -> Optional[MemoryItem]:
        # Get recent active memories to reflect on
        recent_memories = await self.repository.get_recent_active_memories(user_id, limit=50)
        if not recent_memories:
            return None

        content = "\n".join([f"- [{m.memory_type}] {m.title}: {m.content}" for m in recent_memories])

        provider, model = await self.router.get_provider_for_role(LLMRole.SUMMARIZER)

        system_prompt = (
            "You are a reflection engine. Review the user's recent memories and extract a single, "
            "high-level semantic reflection about their current focus, learning path, or broad preferences. "
            "Keep it to one sentence."
        )

        try:
            reflection_text = await provider.complete(
                messages=[{"role": "user", "content": content}],
                model=model,
                system_prompt=system_prompt
            )

            # Create a reflection memory
            candidate = MemoryCreate(
                user_id=user_id,
                memory_type="reflection",
                title="Semantic Reflection",
                content=reflection_text,
                summary="Reflected from recent memories",
                importance_score=0.9,
                confidence_score=0.8,
                source="reflection"
            )

            # Note: In a full pipeline, we might queue an embedding task for this
            created = await self.writer.write(candidate)
            logger.info("memory_reflection_completed", memory_id=str(created.id))
            return created
        except Exception as e:
            logger.error("memory_reflection_failed", error=str(e))
            return None
