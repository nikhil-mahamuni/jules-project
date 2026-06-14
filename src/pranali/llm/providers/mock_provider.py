import asyncio
from typing import AsyncIterator, List, Optional
from src.pranali.llm.provider import LLMProvider
from src.pranali.llm.types import Message

class MockProvider(LLMProvider):
    async def complete(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        # Check if it's used for memory extraction
        if "mock-memory" in model:
            return '[{"memory_type": "fact", "title": "Mock Memory", "content": "This is a mock memory.", "summary": "Mock summary", "entities": ["mock"], "tags": ["mock"], "importance_score": 0.8, "confidence_score": 0.9, "emotional_weight": 0.1, "sensitive": false, "confirmed": true}]'
        return "This is a deterministic mock response."

    async def stream(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> AsyncIterator[str]:
        response = "This is a deterministic mock streaming response."
        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.01)

    async def embed(self, text: str, model: str) -> List[float]:
        # Return a deterministic 1536-dimensional mock embedding
        return [0.01] * 1536

    async def health_check(self) -> bool:
        return True
