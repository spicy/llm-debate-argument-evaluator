import asyncio

from utils.logger import log_execution_time, logger


class AsyncProcessingService:
    def __init__(self):
        self.tasks = []
        logger.info("AsyncProcessingService initialized")

    async def process_async(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.tasks.append(task)
        logger.debug(f"Added new task: {task.get_name()}")
        return task

    @log_execution_time
    async def wait_for_all(self):
        logger.debug(f"Waiting for {len(self.tasks)} tasks to complete")
        await asyncio.gather(*self.tasks)
        logger.debug("All tasks completed")
        self.tasks.clear()
