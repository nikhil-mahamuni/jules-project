from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import User, AssistantIdentity
from src.pranali.config import settings
from src.pranali.utils.time import now

async def seed_default_data(session: AsyncSession) -> None:
    # Check for default user
    result = await session.execute(select(User).limit(1))
    user = result.scalars().first()
    if not user:
        user = User(
            display_name=settings.user.default_display_name,
            timezone=settings.user.timezone,
            locale=settings.user.locale
        )
        session.add(user)

    # Check for default assistant identity
    result = await session.execute(select(AssistantIdentity).limit(1))
    identity = result.scalars().first()
    if not identity:
        identity = AssistantIdentity(
            assistant_name=settings.assistant.name,
            persona_summary=settings.assistant.persona_summary,
            communication_style=settings.assistant.communication_style,
            limitations=settings.assistant.limitations,
            active=True
        )
        session.add(identity)

    await session.commit()
