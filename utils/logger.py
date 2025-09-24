"""
TODO: This module...
"""

import logging
import os
import time
from functools import wraps
from typing import Any, Callable

import colorlog

from config.environment import environment_config
from config.logger_config import logger_config


def setup_logger(config=logger_config) -> logging.Logger:
    """
    Sets up and configures the logger with colored output for console
    and regular output for file logging.
    Thread-safe configuration for multi-threaded applications.
    """
    logger = logging.getLogger(config.LOGGER_NAME)

    # Only configure if not already configured (prevent duplicate handlers in threads)
    if logger.handlers:
        return logger

    if environment_config.DEBUG_MODE:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Console Handler with colors
    console_handler = colorlog.StreamHandler()
    color_formatter = colorlog.ColoredFormatter(
        config.COLOR_LOG_FORMAT, log_colors=config.COLOR_SCHEME, reset=True, style="%"
    )
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)

    # File Handler (without colors)
    os.makedirs(config.LOGS_FOLDER, exist_ok=True)
    file_formatter = logging.Formatter(config.LOG_FORMAT)

    file_handler = logging.FileHandler(
        os.path.join(config.LOGS_FOLDER, config.LOG_FILE_NAME)
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Current session log
    last_path = os.path.join(config.LOGS_FOLDER, config.LAST_FILE_NAME)

    # Try to remove existing session log, but don't fail if it's in use
    if os.path.exists(last_path):
        try:
            os.remove(last_path)
        except (PermissionError, OSError) as e:
            # If we can't remove it, just append to it instead
            print(f"Warning: Could not remove existing log file {last_path}: {e}")

    session_handler = logging.FileHandler(last_path)
    session_handler.setFormatter(file_formatter)
    logger.addHandler(session_handler)

    # Enable propagation to ensure thread logs are captured
    logger.propagate = True

    return logger


def ensure_logger_in_thread(config=logger_config) -> logging.Logger:
    """
    Ensures logger is properly configured in the current thread.
    Call this at the start of any thread that needs logging.
    """
    return setup_logger(config)


def log_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that logs the execution time of a function.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """TODO: Add Simple Docstring"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result

    return wrapper


logger = setup_logger()
