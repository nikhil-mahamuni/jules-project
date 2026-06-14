from src.pranali.memory.context_builder import ContextBuilder
from src.pranali.db.models import AssistantIdentity, Goal
from src.pranali.memory.schemas import RetrievedMemory
import uuid
from datetime import datetime

def test_context_builder():
    builder = ContextBuilder()

    identity = AssistantIdentity(
        persona_summary="A helpful AI.",
        communication_style="Friendly",
        limitations="Cannot browse the internet."
    )

    memories = [
        RetrievedMemory(
            id=uuid.uuid4(),
            memory_type="fact",
            title="User likes coffee",
            content="User drinks black coffee.",
            importance_score=0.8,
            recency_score=1.0,
            final_score=0.9,
            created_at=datetime.now()
        )
    ]

    goals = [
        Goal(title="Learn Python", description="User is learning Python.")
    ]

    buffer = [{"role": "user", "content": "Hi"}]

    context = builder.build(identity, "TestUser", memories, goals, buffer, "How are you?")

    assert "Friendly" in context["system_kwargs"]["communication_style"]
    assert "User drinks black coffee" in context["system_kwargs"]["retrieved_memories"]
    assert "Learn Python" in context["system_kwargs"]["active_goals"]
    assert "User: Hi" in context["recent_turns"]
