import time
from typing import Optional, Dict, Tuple
from src.pranali.cache.store import CacheStore

class InMemoryCacheStore(CacheStore):
    def __init__(self):
        self._cache: Dict[str, Tuple[str, Optional[float]]] = {}

    async def get(self, key: str) -> Optional[str]:
        if key in self._cache:
            value, expires_at = self._cache[key]
            if expires_at and time.time() > expires_at:
                del self._cache[key]
                return None
            return value
        return None

    async def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    async def health_check(self) -> bool:
        return True
