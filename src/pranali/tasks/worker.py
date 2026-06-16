import asyncio
import structlog
from typing import Callable, Coroutine, Dict, Any, Optional
from src.pranali.tasks.queue import InProcessTaskQueue
from src.pranali.tasks.schemas import BackgroundTask
from src.pranali.utils.time import now

logger = structlog.get_logger(__name__)

# Registry mapping task_type string to a handler function
# Handler signature: async def handler(payload: Dict[str, Any]) -> None
TaskHandler = Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]

class TaskWorker:
    def __init__(self, worker_id: int, queue: InProcessTaskQueue, handlers: Dict[str, TaskHandler]):
        self.worker_id = worker_id
        self.queue = queue
        self.handlers = handlers
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

    async def _run(self):
        logger.info("task_worker_started", worker_id=self.worker_id)
        while not self._stop_event.is_set():
            try:
                # Use wait_for to allow checking stop_event periodically
                task_obj = await asyncio.wait_for(self.queue.dequeue(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            await self._process_task(task_obj)
            self.queue.task_done()

        logger.info("task_worker_stopped", worker_id=self.worker_id)

    async def _process_task(self, task: BackgroundTask):
        task.started_at = now()
        task.attempt_count += 1
        logger.debug("processing_task", worker_id=self.worker_id, task_id=str(task.task_id), type=task.task_type.value)

        handler = self.handlers.get(task.task_type.value)
        if not handler:
            logger.error("missing_handler_for_task", type=task.task_type.value)
            return

        try:
            await handler(task.payload)
            task.completed_at = now()
            task.status = "completed"
            logger.info("task_completed", task_id=str(task.task_id), type=task.task_type.value)
        except Exception as e:
            task.error_message = str(e)
            logger.error("task_failed", task_id=str(task.task_id), error=str(e), attempt=task.attempt_count)
            if task.attempt_count < task.max_retries:
                # Re-enqueue for retry with simple backoff
                await asyncio.sleep(2 ** task.attempt_count)
                task.status = "pending"
                await self.queue.enqueue(task)
            else:
                task.status = "failed"
                logger.error("task_max_retries_exceeded", task_id=str(task.task_id))

    def start(self):
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._stop_event.set()
        if self._task:
            await self._task
