import os
from typing import AsyncIterator, List, Optional
import anthropic
from src.pranali.llm.provider import LLMProvider
from src.pranali.llm.types import Message
from src.pranali.utils.errors import ProviderCapabilityError

class AnthropicProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None

    async def health_check(self) -> bool:
        return self.client is not None

    async def complete(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        if not self.client:
            raise ProviderCapabilityError("Anthropic API key missing")

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self.client.messages.create(**kwargs)
        return response.content[0].text

    async def stream(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> AsyncIterator[str]:
        if not self.client:
            raise ProviderCapabilityError("Anthropic API key missing")

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, text: str, model: str) -> List[float]:
        raise ProviderCapabilityError("Anthropic provider does not support embeddings directly in this context.")
