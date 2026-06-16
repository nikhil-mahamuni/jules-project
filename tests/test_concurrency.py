import pytest
import asyncio
import uuid
from src.pranali.concurrency.executors import ThreadPoolManager
from src.pranali.concurrency.locks import LockManager
from src.pranali.concurrency.shutdown import ShutdownCoordinator

def blocking_fake_audio_task():
    import time
    time.sleep(0.1)
    return "audio done"

@pytest.mark.asyncio
async def test_thread_pool_executor():
    pool = ThreadPoolManager(max_workers=2)
    # Ensure blocking audio doesn't block the event loop
    result = await pool.run_in_thread(blocking_fake_audio_task)
    assert result == "audio done"
    pool.shutdown()

@pytest.mark.asyncio
async def test_lock_manager():
    manager = LockManager()
    session_id = uuid.uuid4()

    lock1 = manager.get_session_lock(session_id)
    lock2 = manager.get_session_lock(session_id)

    # Must be the exact same lock object for the same session
    assert lock1 is lock2

    # Simple acquisition test
    async with lock1:
        assert lock1.locked()

@pytest.mark.asyncio
async def test_graceful_shutdown():
    coordinator = ShutdownCoordinator()

    async def dummy_task():
        await asyncio.sleep(0.1)

    task = asyncio.create_task(dummy_task())
    coordinator.register_task(task)

    assert len(coordinator._tasks) == 1
    await coordinator.trigger_shutdown()
    assert coordinator.is_shutting_down
    assert len(coordinator._tasks) == 0
