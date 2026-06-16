import structlog
from typing import Optional
from src.pranali.cache.store import CacheStore

logger = structlog.get_logger(__name__)

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

class RedisCacheStore(CacheStore):
    def __init__(self, redis_url: str):
        if not redis:
            raise ImportError("redis package is not installed.")
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error("redis_get_failed", error=str(e), key=key)
            return None

    async def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        try:
            await self.redis.set(key, value, ex=ttl_seconds)
        except Exception as e:
            logger.error("redis_set_failed", error=str(e), key=key)

    async def delete(self, key: str) -> None:
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error("redis_delete_failed", error=str(e), key=key)

    async def health_check(self) -> bool:
        try:
            return await self.redis.ping()
        except Exception:
            return False
