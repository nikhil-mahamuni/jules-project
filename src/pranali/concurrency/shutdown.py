import asyncio
import structlog
from typing import Set

logger = structlog.get_logger(__name__)

class ShutdownCoordinator:
    def __init__(self):
        self._is_shutting_down = False
        self._tasks: Set[asyncio.Task] = set()

    def register_task(self, task: asyncio.Task):
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    @property
    def is_shutting_down(self) -> bool:
        return self._is_shutting_down

    async def trigger_shutdown(self):
        logger.info("triggering_graceful_shutdown")
        self._is_shutting_down = True

        if self._tasks:
            logger.info("waiting_for_background_tasks", count=len(self._tasks))
            await asyncio.gather(*self._tasks, return_exceptions=True)
            logger.info("background_tasks_completed")
