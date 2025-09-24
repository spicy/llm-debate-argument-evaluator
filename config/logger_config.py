"""
TODO: This module...
"""

from typing import Dict

from config.base_config import BaseConfig


class LoggerConfig(BaseConfig):
    LOGGER_NAME: str = "llm_tree_evaluator"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    COLOR_LOG_FORMAT: str = (
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s"
    )
    LOGS_FOLDER: str = "logs"
    LAST_FILE_NAME: str = "last.log"
    LOG_FILE_NAME: str = "app.log"

    # Color scheme for different log levels
    COLOR_SCHEME: Dict[str, str] = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    }


logger_config: LoggerConfig = LoggerConfig()
