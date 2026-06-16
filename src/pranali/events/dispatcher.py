import asyncio
import structlog
from typing import List, Optional
from src.pranali.events.bus import InProcessEventBus
from src.pranali.events.schemas import PranaliEvent
from src.pranali.config import settings

logger = structlog.get_logger(__name__)

class EventDispatcher:
    def __init__(self, bus: InProcessEventBus):
        self.bus = bus
        self._workers: List[asyncio.Task] = []
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        self._stop_event.clear()
        for i in range(settings.events.dispatcher_workers):
            task = asyncio.create_task(self._worker_loop(i))
            self._workers.append(task)
        logger.info("event_dispatcher_started", workers=len(self._workers))

    async def stop(self) -> None:
        self._stop_event.set()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        logger.info("event_dispatcher_stopped")

    async def _worker_loop(self, worker_id: int) -> None:
        while not self._stop_event.is_set():
            try:
                # wait_for allows periodic checking of stop_event
                event = await asyncio.wait_for(self.bus._dequeue(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            await self._dispatch(event)
            self.bus.task_done()

    async def _dispatch(self, event: PranaliEvent) -> None:
        handlers = self.bus._subscribers.get(event.event_type.value, [])
        if not handlers:
            logger.debug("no_handlers_for_event", type=event.event_type.value)
            return

        logger.debug("event_dispatched", event_id=str(event.event_id), type=event.event_type.value, handlers=len(handlers))

        # Concurrently execute all registered handlers for this event
        tasks = []
        for handler in handlers:
            tasks.append(self._safe_execute(handler, event))

        await asyncio.gather(*tasks)
        logger.debug("event_completed", event_id=str(event.event_id))

    async def _safe_execute(self, handler, event: PranaliEvent):
        try:
            await handler(event)
        except Exception as e:
            logger.error("event_failed", event_id=str(event.event_id), type=event.event_type.value, handler=handler.__name__, error=str(e), exc_info=True)
