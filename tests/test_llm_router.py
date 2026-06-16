import pytest
from src.pranali.llm.router import LLMRouter
from src.pranali.llm.roles import LLMRole
from src.pranali.llm.providers.mock_provider import MockProvider
from src.pranali.llm.providers.anthropic_provider import AnthropicProvider

@pytest.mark.asyncio
async def test_llm_router_fallback():
    router = LLMRouter()
    provider, model = await router.get_provider_for_role(LLMRole.CONVERSATION)

    # Since we don't have ANTHROPIC_API_KEY set in tests, the Anthropic health_check will fail
    # and it should fallback to mock
    assert isinstance(provider, MockProvider)
    assert model == "mock-conversation"

@pytest.mark.asyncio
async def test_llm_router_mock_classifier():
    router = LLMRouter()
    provider, model = await router.get_provider_for_role(LLMRole.CLASSIFIER)
    assert isinstance(provider, MockProvider)
    assert model == "mock-classifier"
