import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.models import EventLog

class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID, session_id: Optional[uuid.UUID], event_type: str, content: str, role: Optional[str] = None, source: str = "conversation", raw_payload: dict = None) -> EventLog:
        event = EventLog(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            content=content,
            role=role,
            source=source,
            raw_payload=raw_payload or {}
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event
