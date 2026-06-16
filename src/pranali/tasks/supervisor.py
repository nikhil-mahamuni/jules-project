import asyncio
import structlog
from typing import Dict, Any, Callable, Coroutine, List
from src.pranali.tasks.types import TaskType, TaskPriority
from src.pranali.tasks.schemas import BackgroundTask
from src.pranali.tasks.queue import InProcessTaskQueue
from src.pranali.tasks.worker import TaskWorker, TaskHandler
from src.pranali.config import settings

logger = structlog.get_logger(__name__)

class TaskSupervisor:
    def __init__(self):
        self.queue = InProcessTaskQueue()
        self.handlers: Dict[str, TaskHandler] = {}
        self.workers: List[TaskWorker] = []
        self._is_running = False

    def register_handler(self, task_type: TaskType, handler: TaskHandler):
        self.handlers[task_type.value] = handler

    def is_running(self) -> bool:
        return self._is_running

    async def start(self):
        if self._is_running or not settings.tasks.enabled:
            return

        self._is_running = True
        for i in range(settings.tasks.worker_count):
            worker = TaskWorker(worker_id=i, queue=self.queue, handlers=self.handlers)
            self.workers.append(worker)
            worker.start()
        logger.info("task_supervisor_started", workers=len(self.workers))

    async def stop(self):
        if not self._is_running:
            return

        logger.info("task_supervisor_stopping")
        self._is_running = False
        await asyncio.gather(*(worker.stop() for worker in self.workers))
        self.workers.clear()
        logger.info("task_supervisor_stopped")

    async def enqueue(self, task_type: TaskType, payload: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL) -> str:
        if not settings.tasks.enabled:
            logger.warning("task_enqueued_but_tasks_disabled", type=task_type.value)

        task = BackgroundTask(
            task_type=task_type,
            payload=payload,
            priority=priority,
            max_retries=settings.tasks.max_retries
        )
        await self.queue.enqueue(task)
        return str(task.task_id)

    def get_queue_size(self) -> int:
        return self.queue.qsize()
