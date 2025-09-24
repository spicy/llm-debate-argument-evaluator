"""
TODO: This module...
"""

from typing import Any, Dict, List, Optional

from config import memoization_config
from infrastructure.caching.cache_manager import CacheManager
from infrastructure.caching.embedding_service import EmbeddingService
from infrastructure.caching.vector_db.base_vector_db_service import BaseVectorDBService
from utils.logger import log_execution_time, logger


class MemoizationService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        cache_manager: CacheManager,
        vector_db_service: BaseVectorDBService,
        similarity_threshold: float = memoization_config.SIMILARITY_THRESHOLD,
    ):
        """TODO: Add Simple Docstring"""
        self.embedding_service = embedding_service
        self.cache_manager = cache_manager
        self.vector_db_service = vector_db_service
        self.similarity_threshold = similarity_threshold
        logger.info(
            f"MemoizationService initialized with similarity threshold: {self.similarity_threshold}"
        )

    def _create_cache_key(self, argument: str, model_names: List[str]) -> str:
        """Create a consistent cache key from the argument and sorted model names."""
        return f"{argument}::{'|'.join(sorted(model_names))}"

    @log_execution_time
    async def get_cached_evaluation(
        self, argument: str, model_names: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get a cached evaluation for a given argument.

        First, it checks for an exact match in the key-value cache. If no exact
        match is found, it performs a semantic similarity search using the
        vector database to find a sufficiently similar argument.
        """
        logger.debug(f"Searching for cached evaluation for: '{argument[:50]}...'")
        cache_key = self._create_cache_key(argument, model_names)

        # First, check for an exact match
        exact_match = self.cache_manager.retrieve(cache_key)
        if exact_match:
            logger.info(f"Cache hit (exact match) for: '{argument[:50]}...'")
            return exact_match

        # Fallback to semantic similarity search using the vector database
        logger.debug(
            "No exact match found. Performing semantic similarity search via vector DB."
        )
        embedding = self.embedding_service.get_embedding(argument)
        similar_cache_key = self.vector_db_service.search(
            embedding, limit=1, threshold=self.similarity_threshold
        )

        if similar_cache_key:
            logger.info(
                f"Cache hit (semantic match) for: '{argument[:50]}...'. Found similar entry with key: {similar_cache_key}"
            )
            evaluation = self.cache_manager.retrieve(similar_cache_key)
            if evaluation:
                # Cache the new argument with the found evaluation for faster access next time
                await self.cache_evaluation(argument, model_names, evaluation)
            return evaluation

        logger.info(f"Cache miss for: '{argument[:50]}...'")
        return None

    @log_execution_time
    async def cache_evaluation(
        self, argument: str, model_names: List[str], evaluation: Dict[str, Any]
    ) -> None:
        """
        Cache an evaluation in the key-value store and add its vector to the vector DB.
        """
        cache_key = self._create_cache_key(argument, model_names)

        # Store textual evaluation data in the JSON cache
        self.cache_manager.store(cache_key, evaluation)

        # Add the argument's vector to the vector database for semantic search
        embedding = self.embedding_service.get_embedding(argument)
        self.vector_db_service.add(
            texts=[argument],
            embeddings=[embedding],
            ids=[cache_key],
            metadatas=[{"models": "|".join(sorted(model_names))}],
        )

        logger.debug(
            f"Cached evaluation for: '{argument[:50]}...' with models {model_names}"
        )
