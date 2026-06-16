import structlog
from src.pranali.db.models import MemoryItem

logger = structlog.get_logger(__name__)

class MemoryConfirmation:
    def needs_confirmation(self, memory: MemoryItem) -> bool:
        # If it's an important memory but confidence is low, it needs confirmation
        return not memory.confirmed and memory.importance_score >= 0.8 and memory.confidence_score < 0.6

    def generate_confirmation_question(self, memory: MemoryItem) -> str:
        return f"Just to confirm, {memory.content.lower()} Is that correct?"
