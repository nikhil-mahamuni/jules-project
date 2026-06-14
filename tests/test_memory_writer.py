import pytest
import uuid
from typing import Optional, List
from unittest.mock import MagicMock, AsyncMock

from src.pranali.db.models import User, MemoryItem
from src.pranali.memory.writer import MemoryWriter
from src.pranali.memory.schemas import MemoryCreate

class MockMemoryRepository:
    def __init__(self):
        self.memories = []

    async def get_by_exact_match(self, user_id: uuid.UUID, memory_type: str, title: str) -> Optional[MemoryItem]:
        for m in self.memories:
            if m.user_id == user_id and m.memory_type == memory_type and m.title == title:
                return m
        return None

    async def get_similar_for_deduplication(self, user_id: uuid.UUID, memory_type: str, embedding: List[float], similarity_threshold: float = 0.85) -> Optional[MemoryItem]:
        # Mock behavior for vector deduplication test
        for m in self.memories:
            # We mock that an embedding match is found if the title starts with "Vector Match"
            if m.user_id == user_id and m.memory_type == memory_type and "Vector Match" in m.title:
                return m
        return None

    async def create(self, memory: MemoryItem) -> MemoryItem:
        if not memory.id:
            memory.id = uuid.uuid4()
        if not memory.version:
            memory.version = 1
        self.memories.append(memory)
        return memory

    async def update(self, memory: MemoryItem) -> MemoryItem:
        return memory

@pytest.mark.asyncio
async def test_memory_writer_create_and_update():
    # Setup mock repository
    mock_repo = MockMemoryRepository()

    # We monkeypatch the writer's repository directly
    writer = MemoryWriter(session=MagicMock())
    writer.repository = mock_repo

    user_id = uuid.uuid4()

    # Test creation
    create_dto = MemoryCreate(
        user_id=user_id,
        memory_type="fact",
        title="Fact 1",
        content="Content 1",
        summary="Summary 1",
        importance_score=0.6,
        confidence_score=0.5
    )

    mem1 = await writer.write(create_dto, embedding=[0.1]*1536)
    assert mem1.id is not None
    assert mem1.version == 1
    assert mem1.title == "Fact 1"

    # Test duplicate update
    update_dto = MemoryCreate(
        user_id=user_id,
        memory_type="fact",
        title="Fact 1",
        content="Content 1 updated",
        summary="Summary 1",
        importance_score=0.8,
        confidence_score=0.5
    )

    mem2 = await writer.write(update_dto, embedding=[0.2]*1536)
    assert mem2.id == mem1.id
    assert mem2.version == 2
    assert mem2.content == "Content 1 updated"
    assert mem2.importance_score == 0.8
    assert mem2.confidence_score > 0.5 # Boosted

    # Test vector similarity deduplication
    vector_dto = MemoryCreate(
        user_id=user_id,
        memory_type="fact",
        title="Vector Match Initial",
        content="This will be matched by vector",
        summary="Summary 3",
        importance_score=0.5,
        confidence_score=0.5
    )
    mem3 = await writer.write(vector_dto, embedding=[0.3]*1536)
    assert mem3.id is not None
    assert mem3.version == 1

    vector_update_dto = MemoryCreate(
        user_id=user_id,
        memory_type="fact",
        title="Different Title but Vector Matches",
        content="Updated vector match content",
        summary="Summary 4",
        importance_score=0.5,
        confidence_score=0.5
    )
    # The mock returns the existing memory if it sees "Vector Match" in title,
    # but since our write logic passes the embedding, our mock intercepts get_similar_for_deduplication
    mem4 = await writer.write(vector_update_dto, embedding=[0.3]*1536)
    assert mem4.id == mem3.id
    assert mem4.version == 2
