import pytest
from src.pranali.llm.router import LLMRouter
from src.pranali.memory.extractor import MemoryExtractor

@pytest.mark.asyncio
async def test_memory_extractor_valid_json():
    router = LLMRouter()
    extractor = MemoryExtractor(router)

    # MockProvider returns valid JSON for "mock-memory" model
    candidates = await extractor.extract("TestUser", "User: I like pizza")

    assert len(candidates) == 1
    assert candidates[0].memory_type == "fact"
    assert candidates[0].title == "Mock Memory"

@pytest.mark.asyncio
async def test_memory_extractor_fallback():
    router = LLMRouter()
    extractor = MemoryExtractor(router)

    # We test the protected fallback method directly
    candidates = extractor._safe_fallback_extraction("User: Remember that my favorite color is blue.")
    assert len(candidates) == 1
    assert candidates[0].memory_type == "fact"
    assert candidates[0].title == "Fallback Extracted Fact"

def test_memory_prompt_secret_filtering():
    from src.pranali.prompts.memory_prompts import build_memory_extraction_prompt
    prompt = build_memory_extraction_prompt("TestUser", "User: Here is my password: 12345")
    # Verify the prompt explicitly instructs the LLM not to store secrets
    assert "API keys" in prompt
    assert "passwords" in prompt
    assert "secrets" in prompt
