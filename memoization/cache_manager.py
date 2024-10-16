import json
from typing import Any, Dict

from utils.logger import log_execution_time, logger


class CacheManager:
    def __init__(self, cache_file: str = "argument_cache.json"):
        self.cache_file = cache_file
        self.cache: Dict[str, Any] = self._load_cache()
        logger.info(f"CacheManager initialized with cache file: {cache_file}")

    @log_execution_time
    def _load_cache(self) -> Dict[str, Any]:
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
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)
        logger.info(f"Cache saved to {self.cache_file}")

    @log_execution_time
    def store(self, argument: str, evaluation: Dict[str, Any]) -> None:
        self.cache[argument] = evaluation
        self._save_cache()
        logger.debug(f"Stored evaluation for argument: '{argument[:50]}...'")

    @log_execution_time
    def retrieve(self, argument: str) -> Dict[str, Any] | None:
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
        logger.debug(f"Retrieving all {len(self.cache)} cached arguments")
        return self.cache
