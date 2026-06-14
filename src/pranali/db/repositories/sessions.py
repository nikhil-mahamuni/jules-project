import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.pranali.db.models import Session

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID, title: str, status: str = "active") -> Session:
        db_session = Session(user_id=user_id, title=title, status=status)
        self.session.add(db_session)
        await self.session.commit()
        await self.session.refresh(db_session)
        return db_session

    async def get(self, session_id: uuid.UUID) -> Optional[Session]:
        result = await self.session.execute(select(Session).where(Session.id == session_id))
        return result.scalars().first()
