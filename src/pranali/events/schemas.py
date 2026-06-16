import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from src.pranali.utils.time import now
from .types import EventType, EventSource, EventPriority

class PranaliEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: Optional[uuid.UUID] = None
    session_id: Optional[uuid.UUID] = None
    event_type: EventType
    source: EventSource
    content: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    correlation_id: Optional[uuid.UUID] = None
    causation_id: Optional[uuid.UUID] = None
    idempotency_key: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
