import uuid
import structlog
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.config import settings
from src.pranali.llm.router import LLMRouter
from src.pranali.llm.roles import LLMRole
from src.pranali.memory.schemas import MemoryCreate, RetrievedMemory
from src.pranali.memory.extractor import MemoryExtractor
from src.pranali.memory.writer import MemoryWriter
from src.pranali.memory.retriever import MemoryRetriever
from src.pranali.memory.vector import VectorService

logger = structlog.get_logger(__name__)

class MemoryService:
    def __init__(self, session: AsyncSession, router: LLMRouter):
        self.session = session
        self.router = router
        self.extractor = MemoryExtractor(router)
        self.writer = MemoryWriter(session)
        self.retriever = MemoryRetriever(session)
        self.vector_service = VectorService(router)

    async def retrieve_context_for_message(self, user_id: uuid.UUID, message: str) -> List[RetrievedMemory]:
        logger.info("memory_retrieval_started", user_id=str(user_id))
        embedding = await self.vector_service.get_embedding(message)
        memories = await self.retriever.retrieve(user_id, top_k=settings.memory.top_k, embedding=embedding)
        logger.info("memory_retrieval_completed", count=len(memories))
        return memories

    async def extract_and_store_from_turn(self, user_id: uuid.UUID, user_name: str, recent_turns: str, source_event_id: Optional[uuid.UUID] = None) -> None:
        if not settings.memory.extraction_enabled:
            return

        logger.info("memory_extraction_started", user_id=str(user_id))
        candidates = await self.extractor.extract(user_name, recent_turns)

        for candidate in candidates:
            if candidate.importance_score >= settings.memory.min_importance_to_store and \
               candidate.confidence_score >= settings.memory.min_confidence_to_store:

                # Get embedding
                embedding = None
                embedding_model = None

                provider, model = await self.router.get_provider_for_role(LLMRole.EMBEDDER)

                try:
                    embedding = await provider.embed(candidate.content, model)
                    embedding_model = model
                except Exception as e:
                    logger.error("embedding_failed_during_write", error=str(e))

                create_dto = MemoryCreate(
                    user_id=user_id,
                    source_event_id=source_event_id,
                    **candidate.model_dump()
                )
                await self.writer.write(create_dto, embedding=embedding, embedding_model=embedding_model)

        logger.info("memory_extraction_completed", candidates=len(candidates))

    async def list_recent_memories(self, user_id: uuid.UUID, limit: int = 10) -> List[RetrievedMemory]:
        return await self.retriever.retrieve(user_id, top_k=limit)
