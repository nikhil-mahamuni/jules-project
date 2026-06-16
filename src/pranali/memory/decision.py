from enum import Enum
from typing import List, Dict, Any, Optional
from src.pranali.memory.schemas import MemoryCandidate
from src.pranali.db.models import Goal
import structlog

logger = structlog.get_logger(__name__)

class MemoryDecision(str, Enum):
    IGNORE = "IGNORE"
    EVENT_ONLY = "EVENT_ONLY"
    CREATE_MEMORY = "CREATE_MEMORY"
    UPDATE_EXISTING = "UPDATE_EXISTING"
    CREATE_GOAL = "CREATE_GOAL"
    CREATE_TASK = "CREATE_TASK"
    CREATE_PREFERENCE = "CREATE_PREFERENCE"
    ASK_CONFIRMATION = "ASK_CONFIRMATION"
    MARK_SENSITIVE = "MARK_SENSITIVE"
    ARCHIVE_OLD = "ARCHIVE_OLD"
    PROMOTE_TO_REFLECTION = "PROMOTE_TO_REFLECTION"

class DecisionEngine:
    def decide(self, candidate: MemoryCandidate, similar_memories: List[Any], active_goals: List[Goal], input_mode: str = "text") -> MemoryDecision:
        # Ignore secrets explicitly, just in case extractor misses
        sensitive_keywords = ["password", "token", "api key", "secret", "credential"]
        if any(kw in candidate.content.lower() for kw in sensitive_keywords):
            logger.warning("decision_engine_ignored_secret", title=candidate.title)
            return MemoryDecision.IGNORE

        # Voice transcript with low confidence lowers overall confidence
        if input_mode == "voice":
            candidate.confidence_score *= 0.8

        # Explicit 'remember this'
        if "remember" in candidate.title.lower() or "remember" in candidate.content.lower():
            if candidate.importance_score < 0.8:
                candidate.importance_score = 0.8 # boost explicit instructions
            return MemoryDecision.CREATE_MEMORY

        # Check existing logic
        if similar_memories:
            for existing in similar_memories:
                # Contradiction check: very similar entities/tags but potentially opposing content.
                # A simple check for now:
                if existing.memory_type == candidate.memory_type and existing.title == candidate.title:
                    return MemoryDecision.UPDATE_EXISTING

        # Type based routing
        if candidate.memory_type == "preference":
            return MemoryDecision.CREATE_PREFERENCE
        elif candidate.memory_type == "goal":
            return MemoryDecision.CREATE_GOAL
        elif candidate.memory_type == "task":
            return MemoryDecision.CREATE_TASK

        # Importance based
        if candidate.importance_score < 0.3:
            return MemoryDecision.EVENT_ONLY

        if candidate.importance_score >= 0.8 and candidate.confidence_score < 0.6:
            candidate.confirmed = False
            return MemoryDecision.ASK_CONFIRMATION

        return MemoryDecision.CREATE_MEMORY
