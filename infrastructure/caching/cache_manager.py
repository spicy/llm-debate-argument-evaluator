"""
TODO: This module...
"""

import json
import os
from typing import Any, Dict

from utils.logger import log_execution_time, logger

from config import memoization_config


class CacheManager:
    def __init__(self, cache_file: str = memoization_config.CACHE_FILE_PATH):
        """TODO: Add Simple Docstring"""
        self.cache_file = cache_file
        self._ensure_cache_directory_exists()
        self.cache: Dict[str, Any] = self._load_cache()
        logger.info(f"CacheManager initialized with cache file: {cache_file}")

    def _ensure_cache_directory_exists(self) -> None:
        """Ensure the directory for the cache file exists."""
        directory = os.path.dirname(self.cache_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created cache directory: {directory}")

    @log_execution_time
    def _load_cache(self) -> Dict[str, Any]:
        """TODO: Add Simple Docstring"""
        try:
            with open(self.cache_file, "r") as f:
                cache = json.load(f)
            logger.info(f"Cache loaded from {self.cache_file}")
            return cache
        except FileNotFoundError:
            logger.warning(
                f"Cache file {self.cache_file} not found. Creating a new cache."
            )
            return {}

    @log_execution_time
    def _save_cache(self) -> None:
        """TODO: Add Simple Docstring"""
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)
        logger.info(f"Cache saved to {self.cache_file}")

    @log_execution_time
    def store(self, argument: str, evaluation: Dict[str, Any]) -> None:
        """TODO: Add Simple Docstring"""
        self.cache[argument] = evaluation
        self._save_cache()
        logger.debug(f"Stored evaluation for argument: '{argument[:50]}...'")

    @log_execution_time
    def retrieve(self, argument: str) -> Dict[str, Any] | None:
        """TODO: Add Simple Docstring"""
        evaluation = self.cache.get(argument)
        if evaluation:
            logger.debug(f"Retrieved evaluation for argument: '{argument[:50]}...'")
        else:
            logger.debug(
                f"No cached evaluation found for argument: '{argument[:50]}...'"
            )
        return evaluation

    @log_execution_time
    def get_all_arguments(self) -> Dict[str, Any]:
        """TODO: Add Simple Docstring"""
        logger.debug(f"Retrieving all {len(self.cache)} cached arguments")
        return self.cache
