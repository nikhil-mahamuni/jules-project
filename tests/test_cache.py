import pytest
import asyncio
from src.pranali.cache.memory_cache import InMemoryCacheStore
from src.pranali.cache.redis_cache import RedisCacheStore

@pytest.mark.asyncio
async def test_memory_cache():
    cache = InMemoryCacheStore()

    await cache.set("key1", "val1")
    assert await cache.get("key1") == "val1"

    await cache.delete("key1")
    assert await cache.get("key1") is None

    # test TTL
    await cache.set("key2", "val2", ttl_seconds=1)
    assert await cache.get("key2") == "val2"
    await asyncio.sleep(1.1)
    assert await cache.get("key2") is None

@pytest.mark.asyncio
async def test_redis_cache_fallback():
    # If redis isn't running or available, health check should return False
    # and operations should fail gracefully without crashing
    try:
        cache = RedisCacheStore("redis://localhost:9999/0") # invalid port
        assert await cache.health_check() is False

        await cache.set("test", "test")
        val = await cache.get("test")
        assert val is None
        await cache.delete("test")
    except ImportError:
        pytest.skip("redis library not installed")
