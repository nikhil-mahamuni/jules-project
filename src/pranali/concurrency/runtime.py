import structlog
from src.pranali.config import settings
from .executors import ThreadPoolManager, ProcessPoolManager
from .locks import LockManager
from .shutdown import ShutdownCoordinator

logger = structlog.get_logger(__name__)

class RuntimeManager:
    def __init__(self):
        self.thread_pool = ThreadPoolManager(max_workers=settings.concurrency.thread_pool_workers)
        self.process_pool = ProcessPoolManager(max_workers=settings.concurrency.process_pool_workers)
        self.locks = LockManager(enabled=settings.concurrency.session_lock_enabled)
        self.shutdown_coordinator = ShutdownCoordinator()

    async def shutdown(self):
        logger.info("runtime_manager_shutting_down")
        await self.shutdown_coordinator.trigger_shutdown()
        self.thread_pool.shutdown()
        self.process_pool.shutdown()
        logger.info("runtime_manager_shutdown_complete")
