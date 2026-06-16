import asyncio
from typing import Dict, Optional
import uuid

class LockManager:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._session_locks: Dict[uuid.UUID, asyncio.Lock] = {}
        self._memory_locks: Dict[uuid.UUID, asyncio.Lock] = {}

    def get_session_lock(self, session_id: uuid.UUID) -> asyncio.Lock:
        if session_id not in self._session_locks:
            self._session_locks[session_id] = asyncio.Lock()
        return self._session_locks[session_id]

    def get_memory_lock(self, memory_id: uuid.UUID) -> asyncio.Lock:
        if memory_id not in self._memory_locks:
            self._memory_locks[memory_id] = asyncio.Lock()
        return self._memory_locks[memory_id]
