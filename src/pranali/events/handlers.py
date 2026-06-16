import structlog
from src.pranali.events.schemas import PranaliEvent

logger = structlog.get_logger(__name__)

async def dummy_event_handler(event: PranaliEvent):
    """A sample event handler."""
    logger.info("handled_event", event_id=str(event.event_id), type=event.event_type.value)
