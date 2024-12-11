import asyncio
from typing import Any, Coroutine, List

from utils.logger import log_execution_time, logger


class AsyncProcessingService:
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self.evaluation_queue = asyncio.Queue()
        self.traversal_queue = asyncio.Queue()
        logger.info("AsyncProcessingService initialized")

    async def process_async(self, coroutine: Coroutine) -> asyncio.Task:
        """Process a single coroutine asynchronously"""
        task = asyncio.create_task(coroutine)
        self.tasks.append(task)
        task.add_done_callback(lambda t: self.tasks.remove(t))
        logger.debug(f"Added new task: {task.get_name()}")
        return task

    async def process_batch(self, coroutines: List[Coroutine]) -> List[Any]:
        """Process multiple coroutines concurrently"""
        tasks = [self.process_async(coro) for coro in coroutines]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

    async def queue_evaluation(self, node: dict):
        """Queue a node for evaluation"""
        await self.evaluation_queue.put(node)
        logger.debug(f"Queued node {node['id']} for evaluation")

    async def queue_traversal(self, node_id: str):
        """Queue a node for traversal"""
        await self.traversal_queue.put(node_id)
        logger.debug(f"Queued node {node_id} for traversal")

    @log_execution_time
    async def wait_for_all(self):
        """Wait for all pending tasks to complete"""
        if self.tasks:
            logger.debug(f"Waiting for {len(self.tasks)} tasks to complete")
            await asyncio.gather(*self.tasks, return_exceptions=True)
            logger.debug("All tasks completed")
