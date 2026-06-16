import structlog
from typing import Tuple
from src.pranali.config import settings
from src.pranali.llm.roles import LLMRole
from src.pranali.llm.provider import LLMProvider
from src.pranali.llm.registry import registry
from src.pranali.utils.errors import LLMRouterError

logger = structlog.get_logger(__name__)

class LLMRouter:
    def __init__(self):
        self._initialized = True

    async def get_provider_for_role(self, role: LLMRole) -> Tuple[LLMProvider, str]:
        role_config = settings.llm.roles.get(role.value)
        if not role_config:
            logger.warning("no_role_config", role=role.value, default_provider=settings.llm.default_provider)
            return registry.get(settings.llm.default_provider), "default-model"

        provider = registry.get(role_config.provider)
        if await provider.health_check():
            logger.debug("provider_selected", role=role.value, provider=role_config.provider, model=role_config.model)
            return provider, role_config.model

        # Fallback
        if role_config.fallback_provider:
            fallback_provider = registry.get(role_config.fallback_provider)
            if await fallback_provider.health_check():
                logger.warning("provider_fallback_used", role=role.value, original_provider=role_config.provider, fallback_provider=role_config.fallback_provider)
                return fallback_provider, role_config.fallback_model or "default-model"

        # Final fallback to mock if everything fails
        logger.warning("final_fallback_to_mock", role=role.value)
        return registry.get("mock"), "mock-fallback"
