import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Any, Callable, Coroutine

class ThreadPoolManager:
    def __init__(self, max_workers: int):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def run_in_thread(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, lambda: func(*args, **kwargs))

    def shutdown(self):
        self.executor.shutdown(wait=True)

class ProcessPoolManager:
    def __init__(self, max_workers: int):
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    async def run_in_process(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, lambda: func(*args, **kwargs))

    def shutdown(self):
        self.executor.shutdown(wait=True)
