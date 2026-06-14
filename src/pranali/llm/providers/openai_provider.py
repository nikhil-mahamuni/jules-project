import os
from typing import AsyncIterator, List, Optional
import openai
from src.pranali.llm.provider import LLMProvider
from src.pranali.llm.types import Message
from src.pranali.utils.errors import ProviderCapabilityError

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None

    async def health_check(self) -> bool:
        return self.client is not None

    async def complete(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        if not self.client:
            raise ProviderCapabilityError("OpenAI API key missing")

        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)

        response = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content or ""

    async def stream(self, messages: List[Message], model: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> AsyncIterator[str]:
        if not self.client:
            raise ProviderCapabilityError("OpenAI API key missing")

        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)

        stream = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, text: str, model: str) -> List[float]:
        if not self.client:
            raise ProviderCapabilityError("OpenAI API key missing")
        response = await self.client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
