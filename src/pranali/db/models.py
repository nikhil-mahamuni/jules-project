import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import Base
from src.pranali.utils.time import now

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default='Asia/Kolkata')
    locale = Column(String, nullable=False, default='en-IN')
    metadata_ = Column("metadata", JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), nullable=False, default=now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now, onupdate=now)

class AssistantIdentity(Base):
    __tablename__ = "assistant_identity"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assistant_name = Column(String, nullable=False)
    persona_summary = Column(String, nullable=False)
    communication_style = Column(String, nullable=False)
    limitations = Column(String, nullable=False)
    core_values = Column(JSONB, nullable=False, default=[])
    active = Column(Boolean, nullable=False, default=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now, onupdate=now)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, default=now, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), nullable=False, default=now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now, onupdate=now)

class EventLog(Base):
    __tablename__ = "event_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    role = Column(String, nullable=True)
    content = Column(String, nullable=False)
    raw_payload = Column(JSONB, nullable=False, default={})
    source = Column(String, nullable=False, default='conversation')
    importance_score = Column(Float, nullable=False, default=0.5)
    confidence_score = Column(Float, nullable=False, default=0.5)
    emotional_weight = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now, index=True)

class MemoryItem(Base):
    __tablename__ = "memory_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    memory_type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    entities = Column(JSONB, nullable=False, default=[])
    tags = Column(JSONB, nullable=False, default=[])
    embedding = Column(Vector(1536), nullable=True)
    embedding_model = Column(String, nullable=True)
    importance_score = Column(Float, nullable=False, default=0.5, index=True)
    confidence_score = Column(Float, nullable=False, default=0.5)
    emotional_weight = Column(Float, nullable=False, default=0.0)
    recency_score = Column(Float, nullable=False, default=1.0)
    retrieval_count = Column(Integer, nullable=False, default=0)
    source = Column(String, nullable=False, default='conversation')
    source_event_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now, onupdate=now)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    sensitive = Column(Boolean, nullable=False, default=False)
    confirmed = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True, index=True)
    archived = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)

class Goal(Base):
    __tablename__ = "goals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False, default='')
    status = Column(String, nullable=False, default='active', index=True)
    priority = Column(Float, nullable=False, default=0.5)
    source_memory_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now, onupdate=now)
