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


async def run_with_timeout(coroutine: Coroutine, timeout: float) -> Any:
    """
    Run a coroutine with a timeout.
    """
    try:
        logger.debug(f"Running coroutine with {timeout}s timeout")
        result = await asyncio.wait_for(coroutine, timeout=timeout)
        logger.debug("Coroutine completed within timeout")
        return result
    except asyncio.TimeoutError:
        logger.warning(f"Coroutine timed out after {timeout}s")
        raise
