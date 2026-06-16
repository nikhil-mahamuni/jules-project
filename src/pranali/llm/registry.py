from typing import Dict, Type
from src.pranali.llm.provider import LLMProvider
from src.pranali.llm.providers.mock_provider import MockProvider
from src.pranali.llm.providers.openai_provider import OpenAIProvider
from src.pranali.llm.providers.anthropic_provider import AnthropicProvider

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        self.register("mock", MockProvider())
        self.register("openai", OpenAIProvider())
        self.register("anthropic", AnthropicProvider())

    def register(self, name: str, provider: LLMProvider):
        self._providers[name] = provider

    def get(self, name: str) -> LLMProvider:
        if name not in self._providers:
            # Fallback to mock
            return self._providers["mock"]
        return self._providers[name]

registry = ProviderRegistry()
