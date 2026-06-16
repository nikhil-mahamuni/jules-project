import asyncio
import structlog
from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Dict, List, Any
from .schemas import PranaliEvent
from .types import EventType
from src.pranali.config import settings

logger = structlog.get_logger(__name__)

EventHandler = Callable[[PranaliEvent], Coroutine[Any, Any, None]]

class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: PranaliEvent) -> None:
        pass

    @abstractmethod
    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

import dataclasses

@dataclasses.dataclass(order=True)
class PrioritizedEvent:
    priority: int
    timestamp: float
    event: PranaliEvent = dataclasses.field(compare=False)

class InProcessEventBus(EventBus):
    def __init__(self):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=settings.events.queue_max_size)
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._is_running = False

    async def publish(self, event: PranaliEvent) -> None:
        try:
            item = PrioritizedEvent(event.priority.value, event.created_at.timestamp(), event)
            await self._queue.put(item)
            logger.debug("event_published", event_id=str(event.event_id), type=event.event_type.value)
        except asyncio.QueueFull:
            logger.error("event_bus_queue_full", event_id=str(event.event_id))
            raise

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        type_str = event_type.value
        if type_str not in self._subscribers:
            self._subscribers[type_str] = []
        self._subscribers[type_str].append(handler)

    async def _dequeue(self) -> PranaliEvent:
        item = await self._queue.get()
        return item.event

    def task_done(self):
        self._queue.task_done()

    async def start(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        logger.info("in_process_event_bus_started")

    async def stop(self) -> None:
        if not self._is_running:
            return
        self._is_running = False
        logger.info("in_process_event_bus_stopped")

    async def health_check(self) -> bool:
        return True
