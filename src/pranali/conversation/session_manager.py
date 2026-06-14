import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.pranali.db.models import Session, User, AssistantIdentity
from src.pranali.db.repositories.sessions import SessionRepository
from src.pranali.db.repositories.users import UserRepository
from src.pranali.db.repositories.identity import IdentityRepository
from src.pranali.db.repositories.goals import GoalRepository
from src.pranali.config import settings

class SessionManager:
    def __init__(self, session: AsyncSession):
        self.session_repo = SessionRepository(session)
        self.user_repo = UserRepository(session)
        self.identity_repo = IdentityRepository(session)
        self.goal_repo = GoalRepository(session)

    async def get_or_create_default_user(self) -> User:
        user = await self.user_repo.get_default_user()
        if not user:
            raise ValueError("Default user not found. Did you run init-db?")
        return user

    async def get_active_identity(self) -> AssistantIdentity:
        identity = await self.identity_repo.get_active_identity()
        if not identity:
            raise ValueError("Active identity not found. Did you run init-db?")
        return identity

    async def create_session(self, user_id: uuid.UUID, title: str = "New Chat") -> Session:
        return await self.session_repo.create(user_id, title)
