from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.pranali.db.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_default_user(self) -> Optional[User]:
        result = await self.session.execute(select(User).limit(1))
        return result.scalars().first()
