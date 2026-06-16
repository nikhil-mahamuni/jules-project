import structlog
from typing import List, Optional
from src.pranali.llm.router import LLMRouter
from src.pranali.llm.roles import LLMRole

logger = structlog.get_logger(__name__)

class VectorService:
    def __init__(self, router: LLMRouter):
        self.router = router

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        provider, model = await self.router.get_provider_for_role(LLMRole.EMBEDDER)
        try:
            embedding = await provider.embed(text, model)
            return embedding
        except Exception as e:
            logger.error("embedding_failed", error=str(e), text=text[:50])
            return None
