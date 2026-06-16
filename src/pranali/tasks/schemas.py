from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from src.pranali.utils.time import now
from src.pranali.tasks.types import TaskType, TaskPriority

class BackgroundTask(BaseModel):
    task_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    task_type: TaskType
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    max_retries: int = 3
    attempt_count: int = 0
    status: str = "pending"
    created_at: datetime = Field(default_factory=now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
