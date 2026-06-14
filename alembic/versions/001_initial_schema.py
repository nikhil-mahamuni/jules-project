"""initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-06-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.Column('timezone', sa.String(), nullable=False),
    sa.Column('locale', sa.String(), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('assistant_identity',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('assistant_name', sa.String(), nullable=False),
    sa.Column('persona_summary', sa.String(), nullable=False),
    sa.Column('communication_style', sa.String(), nullable=False),
    sa.Column('limitations', sa.String(), nullable=False),
    sa.Column('core_values', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('sessions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_started_at'), 'sessions', ['started_at'], unique=False)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)

    op.create_table('event_log',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('session_id', sa.UUID(), nullable=True),
    sa.Column('event_type', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('importance_score', sa.Float(), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('emotional_weight', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_log_created_at'), 'event_log', ['created_at'], unique=False)
    op.create_index(op.f('ix_event_log_event_type'), 'event_log', ['event_type'], unique=False)
    op.create_index(op.f('ix_event_log_session_id'), 'event_log', ['session_id'], unique=False)
    op.create_index(op.f('ix_event_log_user_id'), 'event_log', ['user_id'], unique=False)

    op.create_table('memory_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('memory_type', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('summary', sa.String(), nullable=False),
    sa.Column('entities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('embedding', Vector(dim=1536), nullable=True),
    sa.Column('embedding_model', sa.String(), nullable=True),
    sa.Column('importance_score', sa.Float(), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('emotional_weight', sa.Float(), nullable=False),
    sa.Column('recency_score', sa.Float(), nullable=False),
    sa.Column('retrieval_count', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('source_event_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('sensitive', sa.Boolean(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('archived', sa.Boolean(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memory_items_active'), 'memory_items', ['active'], unique=False)
    op.create_index(op.f('ix_memory_items_importance_score'), 'memory_items', ['importance_score'], unique=False)
    op.create_index(op.f('ix_memory_items_last_accessed_at'), 'memory_items', ['last_accessed_at'], unique=False)
    op.create_index(op.f('ix_memory_items_memory_type'), 'memory_items', ['memory_type'], unique=False)
    op.create_index(op.f('ix_memory_items_user_id'), 'memory_items', ['user_id'], unique=False)

    # GIN indexes for JSONB columns
    op.execute('CREATE INDEX ix_memory_items_tags ON memory_items USING GIN (tags);')
    op.execute('CREATE INDEX ix_memory_items_entities ON memory_items USING GIN (entities);')
    # Vector index
    op.execute('CREATE INDEX ix_memory_items_embedding ON memory_items USING hnsw (embedding vector_cosine_ops);')

    op.create_table('goals',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('priority', sa.Float(), nullable=False),
    sa.Column('source_memory_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goals_status'), 'goals', ['status'], unique=False)
    op.create_index(op.f('ix_goals_user_id'), 'goals', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_goals_user_id'), table_name='goals')
    op.drop_index(op.f('ix_goals_status'), table_name='goals')
    op.drop_table('goals')
    op.execute('DROP INDEX ix_memory_items_embedding;')
    op.execute('DROP INDEX ix_memory_items_entities;')
    op.execute('DROP INDEX ix_memory_items_tags;')
    op.drop_index(op.f('ix_memory_items_user_id'), table_name='memory_items')
    op.drop_index(op.f('ix_memory_items_memory_type'), table_name='memory_items')
    op.drop_index(op.f('ix_memory_items_last_accessed_at'), table_name='memory_items')
    op.drop_index(op.f('ix_memory_items_importance_score'), table_name='memory_items')
    op.drop_index(op.f('ix_memory_items_active'), table_name='memory_items')
    op.drop_table('memory_items')
    op.drop_index(op.f('ix_event_log_user_id'), table_name='event_log')
    op.drop_index(op.f('ix_event_log_session_id'), table_name='event_log')
    op.drop_index(op.f('ix_event_log_event_type'), table_name='event_log')
    op.drop_index(op.f('ix_event_log_created_at'), table_name='event_log')
    op.drop_table('event_log')
    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_started_at'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_table('assistant_identity')
    op.drop_table('users')
