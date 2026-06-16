import pytest
import uuid
from typing import Optional, List
from unittest.mock import MagicMock

from src.pranali.memory.decision import DecisionEngine, MemoryDecision
from src.pranali.memory.schemas import MemoryCandidate

def test_decision_engine():
    engine = DecisionEngine()

    # 1. Test secret filtering
    candidate_secret = MemoryCandidate(
        memory_type="fact",
        title="Secret",
        content="my api key is 1234",
        summary="sum",
    )
    assert engine.decide(candidate_secret, [], []) == MemoryDecision.IGNORE

    # 2. Test explicit remember
    candidate_explicit = MemoryCandidate(
        memory_type="fact",
        title="Remember this",
        content="I like dogs",
        summary="sum",
        importance_score=0.1
    )
    decision = engine.decide(candidate_explicit, [], [])
    assert decision == MemoryDecision.CREATE_MEMORY
    assert candidate_explicit.importance_score == 0.8 # Boosted

    # 3. Test low value
    candidate_low = MemoryCandidate(
        memory_type="fact",
        title="low",
        content="ok",
        summary="ok",
        importance_score=0.1
    )
    assert engine.decide(candidate_low, [], []) == MemoryDecision.EVENT_ONLY

    # 4. Test unconfirmed high importance
    candidate_unconfirmed = MemoryCandidate(
        memory_type="fact",
        title="high",
        content="high",
        summary="high",
        importance_score=0.9,
        confidence_score=0.4,
        confirmed=False
    )
    assert engine.decide(candidate_unconfirmed, [], []) == MemoryDecision.ASK_CONFIRMATION
    assert candidate_unconfirmed.confirmed == False

def test_conflict_detection():
    from src.pranali.memory.conflict import MemoryConflictDetector
    from src.pranali.db.models import MemoryItem

    detector = MemoryConflictDetector()

    existing = [
        MemoryItem(
            memory_type="preference",
            title="Favorite Color",
            content="User prefers blue"
        )
    ]

    candidate = MemoryCandidate(
        memory_type="preference",
        title="Favorite Color",
        content="User prefers red",
        summary="sum"
    )

    conflict = detector.detect_conflict(candidate, existing)
    assert conflict is not None
    assert conflict.content == "User prefers blue"

def test_confirmation_generation():
    from src.pranali.memory.confirmation import MemoryConfirmation
    from src.pranali.db.models import MemoryItem

    conf = MemoryConfirmation()
    item = MemoryItem(
        content="User lives in New York",
        importance_score=0.9,
        confidence_score=0.4,
        confirmed=False
    )
    assert conf.needs_confirmation(item) is True
    question = conf.generate_confirmation_question(item)
    assert "user lives in new york" in question
