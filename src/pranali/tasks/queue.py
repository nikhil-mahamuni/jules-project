import asyncio
from typing import Optional
import structlog
from src.pranali.tasks.schemas import BackgroundTask
from src.pranali.config import settings

logger = structlog.get_logger(__name__)

import dataclasses

@dataclasses.dataclass(order=True)
class PrioritizedTask:
    priority: int
    timestamp: float
    task: BackgroundTask = dataclasses.field(compare=False)

class InProcessTaskQueue:
    def __init__(self):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=settings.tasks.queue_max_size)

    async def enqueue(self, task: BackgroundTask) -> None:
        try:
            item = PrioritizedTask(task.priority.value, task.created_at.timestamp(), task)
            await self._queue.put(item)
            logger.debug("task_enqueued", task_id=str(task.task_id), type=task.task_type.value)
        except asyncio.QueueFull:
            logger.error("task_queue_full", task_id=str(task.task_id))
            raise

    async def dequeue(self) -> BackgroundTask:
        item = await self._queue.get()
        return item.task

    def task_done(self):
        self._queue.task_done()

    def qsize(self) -> int:
        return self._queue.qsize()
