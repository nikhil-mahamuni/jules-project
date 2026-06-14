from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional
from src.pranali.llm.types import Message

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate a complete text response."""
        pass

    @abstractmethod
    async def stream(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> AsyncIterator[str]:
        """Generate a streaming text response."""
        pass

    @abstractmethod
    async def embed(self, text: str, model: str) -> List[float]:
        """Generate embeddings for text."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and ready."""
        pass
