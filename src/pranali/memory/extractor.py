import json
import structlog
from typing import List
from src.pranali.llm.router import LLMRouter
from src.pranali.llm.roles import LLMRole
from src.pranali.prompts.memory_prompts import build_memory_extraction_prompt
from src.pranali.memory.schemas import MemoryCandidate

logger = structlog.get_logger(__name__)

class MemoryExtractor:
    def __init__(self, router: LLMRouter):
        self.router = router

    async def extract(self, user_display_name: str, recent_turns: str) -> List[MemoryCandidate]:
        provider, model = await self.router.get_provider_for_role(LLMRole.MEMORY_EXTRACTOR)
        prompt = build_memory_extraction_prompt(user_display_name, recent_turns)

        try:
            response = await provider.complete(
                messages=[],
                model=model,
                system_prompt=prompt,
                temperature=0.1
            )

            # Basic cleanup in case model wrapped json in markdown
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            raw_memories = json.loads(response)
            if not isinstance(raw_memories, list):
                raise ValueError("LLM response is not a JSON array")

            candidates = []
            for item in raw_memories:
                try:
                    candidate = MemoryCandidate(**item)
                    candidates.append(candidate)
                except Exception as e:
                    logger.warning("invalid_memory_candidate", error=str(e), item=item)
            return candidates

        except json.JSONDecodeError as e:
            logger.warning("json_decode_error_in_memory_extraction", error=str(e), response=response)
            return self._safe_fallback_extraction(recent_turns)
        except Exception as e:
            logger.error("memory_extraction_failed", error=str(e))
            return []

    def _safe_fallback_extraction(self, text: str) -> List[MemoryCandidate]:
        # Minimal rule-based fallback if JSON is invalid
        if "remember that" in text.lower() or "my favorite" in text.lower():
            return [MemoryCandidate(
                memory_type="fact",
                title="Fallback Extracted Fact",
                content=text[:200],
                summary="Fallback extraction",
                importance_score=0.5,
                confidence_score=0.5,
                emotional_weight=0.0
            )]
        return []
