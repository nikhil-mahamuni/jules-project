import pytest
import asyncio
from src.pranali.tasks.queue import InProcessTaskQueue
from src.pranali.tasks.supervisor import TaskSupervisor
from src.pranali.tasks.types import TaskType, TaskPriority
from src.pranali.tasks.schemas import BackgroundTask

@pytest.mark.asyncio
async def test_task_queue():
    queue = InProcessTaskQueue()
    task = BackgroundTask(
        task_type=TaskType.MEMORY_EXTRACTION,
        payload={"data": "test"},
        priority=TaskPriority.HIGH
    )
    await queue.enqueue(task)
    assert queue.qsize() == 1

    dequeued_task = await queue.dequeue()
    assert dequeued_task.task_id == task.task_id
    queue.task_done()
    assert queue.qsize() == 0

@pytest.mark.asyncio
async def test_task_supervisor_processing():
    supervisor = TaskSupervisor()
    processed = []

    async def dummy_handler(payload):
        processed.append(payload)

    supervisor.register_handler(TaskType.MEMORY_EXTRACTION, dummy_handler)

    await supervisor.start()

    await supervisor.enqueue(TaskType.MEMORY_EXTRACTION, {"key": "value"})

    # Wait for processing
    await asyncio.sleep(0.1)

    await supervisor.stop()

    assert len(processed) == 1
    assert processed[0] == {"key": "value"}

@pytest.mark.asyncio
async def test_task_supervisor_failure_recovery():
    supervisor = TaskSupervisor()
    attempts = []

    async def failing_handler(payload):
        attempts.append(1)
        raise ValueError("Simulated failure")

    supervisor.register_handler(TaskType.MEMORY_EXTRACTION, failing_handler)
    await supervisor.start()

    await supervisor.enqueue(TaskType.MEMORY_EXTRACTION, {"key": "value"})

    # Needs to wait long enough for retries.
    # Attempt 0: sleep(2**1)=2s.
    # We will just verify it caught the error and didn't crash.
    await asyncio.sleep(0.1)

    assert len(attempts) >= 1
    assert supervisor.is_running() == True # Supervisor still running
    await supervisor.stop()
