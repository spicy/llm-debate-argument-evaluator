"""
TODO: This module...
"""

from config import memoization_config
from infrastructure.asynchronous import AsyncProcessingService
from infrastructure.caching.cache_manager import CacheManager
from infrastructure.caching.embedding_service import EmbeddingService
from infrastructure.caching.memoization_service import MemoizationService
from infrastructure.caching.vector_db.qdrant_service import QdrantService
from infrastructure.database.supabase_service import SupabaseService
from features.tree.tree_repository import TreeRepository

from utils.dependency_registry import DependencyRegistry
from utils.logger import logger


class InfrastructureInjector:
    def __init__(self, registry: DependencyRegistry):
        """TODO: Add Simple Docstring"""
        self.registry = registry

    def inject(self):
        """TODO: Add Simple Docstring"""
        logger.debug("Injecting infrastructure services")

        async_processing_service = AsyncProcessingService()
        self.registry.register("async_processing_service", async_processing_service)

        supabase_service = SupabaseService()
        self.registry.register("supabase_service", supabase_service)

        embedding_service = EmbeddingService()
        self.registry.register("embedding_service", embedding_service)

        qdrant_service = QdrantService(embedding_service=embedding_service)
        self.registry.register("qdrant_service", qdrant_service)

        repository = TreeRepository(supabase_service)
        self.registry.register("tree_repository", repository)

        cache_manager = CacheManager()
        memoization_service = MemoizationService(
            embedding_service=embedding_service,
            cache_manager=cache_manager,
            vector_db_service=qdrant_service,
        )
        self.registry.register("memoization_service", memoization_service)

        logger.info("Infrastructure services injected successfully")
