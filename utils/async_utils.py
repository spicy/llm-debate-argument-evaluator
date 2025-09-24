"""
TODO: This module...
"""

import asyncio
from typing import Any, Coroutine, List

from utils.logger import log_execution_time, logger


@log_execution_time
async def run_async_tasks(tasks: List[Coroutine]) -> List[Any]:
    """
    Run a list of coroutines concurrently and return their results.
    """
    logger.debug(f"Running {len(tasks)} async tasks")
    results = await asyncio.gather(*tasks)
    logger.debug(f"Completed {len(tasks)} async tasks")
    return results
