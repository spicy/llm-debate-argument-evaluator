import logging
import os
import time
from functools import wraps
from typing import Any, Callable
from config.environment import environment_config

from config.logger_config import logger_config


def setup_logger(config=logger_config) -> logging.Logger:
    """
    Sets up and configures the logger.
    """
    logger = logging.getLogger(config.LOGGER_NAME)
    if (environment_config.DEBUG_MODE):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        
    formatter = logging.Formatter(config.LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    os.makedirs(config.LOGS_FOLDER, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(config.LOGS_FOLDER, config.LOG_FILE_NAME)
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def log_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that logs the execution time of a function.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result

    return wrapper


logger = setup_logger()
