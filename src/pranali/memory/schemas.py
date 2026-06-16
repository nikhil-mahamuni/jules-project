import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryCandidate(BaseModel):
    memory_type: str
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    summary: str
    entities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    importance_score: float = Field(ge=0.0, le=1.0, default=0.5)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    emotional_weight: float = Field(ge=0.0, le=1.0, default=0.0)
    sensitive: bool = False
    confirmed: bool = False

class MemoryCreate(MemoryCandidate):
    user_id: uuid.UUID
    source: str = "conversation"
    source_event_id: Optional[uuid.UUID] = None

class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    entities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    importance_score: Optional[float] = None
    confidence_score: Optional[float] = None
    emotional_weight: Optional[float] = None
    version: int

class RetrievedMemory(BaseModel):
    id: uuid.UUID
    memory_type: str
    title: str
    content: str
    importance_score: float
    recency_score: float
    final_score: float
    created_at: datetime

class MemoryExtractionResult(BaseModel):
    candidates: List[MemoryCandidate]
