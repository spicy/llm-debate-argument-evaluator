from typing import Any, Dict

from config import memoization_config
from memoization.cache_manager import CacheManager
from memoization.semantic_similarity import SemanticSimilarity
from utils.logger import log_execution_time, logger


class MemoizationService:
    def __init__(
        self,
        semantic_similarity: SemanticSimilarity,
        cache_manager: CacheManager,
        similarity_threshold: float = memoization_config.SIMILARITY_THRESHOLD,
    ):
        self.semantic_similarity = semantic_similarity
        self.cache_manager = cache_manager
        self.similarity_threshold = similarity_threshold
        logger.info(
            f"MemoizationService initialized with similarity threshold: {self.similarity_threshold}"
        )

    @log_execution_time
    async def get_cached_evaluation(self, argument: str) -> Dict[str, Any] | None:
        logger.debug(f"Searching for cached evaluation: '{argument[:50]}...'")
        cached_arguments = self.cache_manager.get_all_arguments()

        for cached_arg, evaluation in cached_arguments.items():
            similarity = await self.semantic_similarity.calculate_similarity(
                argument, cached_arg
            )
            if similarity >= self.similarity_threshold:
                logger.info(f"Cache hit: similarity {similarity:.2f}")
                return evaluation

        logger.debug("Cache miss")
        return None

    @log_execution_time
    async def cache_evaluation(self, argument: str, evaluation: Dict[str, Any]) -> None:
        logger.debug(f"Caching evaluation for: '{argument[:50]}...'")
        self.cache_manager.store(argument, evaluation)
        logger.debug("Evaluation cached")
