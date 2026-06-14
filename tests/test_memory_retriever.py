import pytest
import uuid
from datetime import datetime
from typing import Optional, List
from unittest.mock import MagicMock

from src.pranali.db.models import MemoryItem
from src.pranali.memory.retriever import MemoryRetriever

class MockMemoryRepository:
    def __init__(self, memories: List[MemoryItem]):
        self.memories = memories

    async def get_recent_active_memories(self, user_id: uuid.UUID, limit: int = 10) -> List[MemoryItem]:
        return self.memories[:limit]

    async def search_similar(self, user_id: uuid.UUID, embedding: List[float], limit: int = 5) -> List[MemoryItem]:
        return self.memories[:limit]

    async def update_many(self, memories: List[MemoryItem]) -> None:
        pass

@pytest.mark.asyncio
async def test_memory_retriever():
    user_id = uuid.uuid4()

    mem1 = MemoryItem(
        id=uuid.uuid4(),
        user_id=user_id,
        memory_type="fact",
        title="Mem 1",
        content="Content 1",
        summary="Sum 1",
        importance_score=0.9,
        confidence_score=0.9,
        emotional_weight=0.1,
        recency_score=1.0,
        active=True,
        created_at=datetime.utcnow(),
        retrieval_count=0
    )
    mem2 = MemoryItem(
        id=uuid.uuid4(),
        user_id=user_id,
        memory_type="fact",
        title="Mem 2",
        content="Content 2",
        summary="Sum 2",
        importance_score=0.4,
        confidence_score=0.5,
        emotional_weight=0.1,
        recency_score=1.0,
        active=True,
        created_at=datetime.utcnow(),
        retrieval_count=0
    )

    mock_repo = MockMemoryRepository([mem1, mem2])

    retriever = MemoryRetriever(session=MagicMock())
    retriever.repository = mock_repo

    # Without embeddings, retrieves recent active and scores them
    results = await retriever.retrieve(user_id, top_k=5)

    assert len(results) == 2
    # mem1 should be ranked higher due to importance score
    assert results[0].title == "Mem 1"
    assert results[1].title == "Mem 2"
