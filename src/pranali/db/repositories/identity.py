from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.pranali.db.models import AssistantIdentity

class IdentityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_identity(self) -> Optional[AssistantIdentity]:
        result = await self.session.execute(
            select(AssistantIdentity).where(AssistantIdentity.active == True).limit(1)
        )
        return result.scalars().first()
