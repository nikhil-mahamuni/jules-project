import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.pranali.db.models import Goal

class GoalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_goals(self, user_id: uuid.UUID) -> List[Goal]:
        result = await self.session.execute(
            select(Goal).where(Goal.user_id == user_id, Goal.status == 'active')
        )
        return list(result.scalars().all())
