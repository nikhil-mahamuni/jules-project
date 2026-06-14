import pytest
import json
from src.pranali.llm.providers.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_mock_provider_complete():
    provider = MockProvider()
    response = await provider.complete(messages=[], model="mock", system_prompt=None)
    assert response == "This is a deterministic mock response."

@pytest.mark.asyncio
async def test_mock_provider_memory_extraction():
    provider = MockProvider()
    response = await provider.complete(messages=[], model="mock-memory", system_prompt=None)
    # Check if it returns valid json list
    data = json.loads(response)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["memory_type"] == "fact"

@pytest.mark.asyncio
async def test_mock_provider_embed():
    provider = MockProvider()
    embed = await provider.embed(text="test", model="mock")
    assert len(embed) == 1536
    assert embed[0] == 0.01

@pytest.mark.asyncio
async def test_mock_provider_stream():
    provider = MockProvider()
    stream = provider.stream(messages=[], model="mock")
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
    assert len(chunks) > 0
    assert "deterministic" in "".join(chunks)
