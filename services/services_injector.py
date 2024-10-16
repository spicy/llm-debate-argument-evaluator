from config import memoization_config
from evaluation.model_factory import ModelFactory
from memoization.cache_manager import CacheManager
from memoization.semantic_similarity import SemanticSimilarity
from services.argument_generation_service import ArgumentGenerationService
from services.async_processing_service import AsyncProcessingService
from services.evaluation_service import EvaluationService
from services.memoization_service import MemoizationService
from services.model_selection_service import ModelSelectionService
from services.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import logger


class ServicesInjector:
    @staticmethod
    def inject_services(registry):
        logger.debug("Injecting services")

        # Initialize core services
        model_factory = ModelFactory()
        registry.register("model_factory", model_factory)

        # Initialize memoization components
        semantic_similarity = SemanticSimilarity(
            memoization_config.SEMANTIC_SIMILARITY_MODEL
        )
        cache_manager = CacheManager(memoization_config.CACHE_FILE_PATH)
        memoization_service = MemoizationService(
            semantic_similarity, cache_manager, memoization_config.SIMILARITY_THRESHOLD
        )

        # Initialize other services
        async_processing_service = AsyncProcessingService()
        evaluation_service = EvaluationService(model_factory)
        model_selection_service = ModelSelectionService(model_factory)
        argument_generation_service = ArgumentGenerationService(
            model_factory.get_model("ChatGPT")
        )
        priority_queue_service = PriorityQueueService()
        score_aggregator_service = ScoreAggregatorService()

        # Register services
        registry.register("async_processing_service", async_processing_service)
        registry.register("memoization_service", memoization_service)
        registry.register("evaluation_service", evaluation_service)
        registry.register("model_selection_service", model_selection_service)
        registry.register("argument_generation_service", argument_generation_service)
        registry.register("priority_queue_service", priority_queue_service)
        registry.register("score_aggregator_service", score_aggregator_service)
        registry.register("semantic_similarity", semantic_similarity)
        registry.register("cache_manager", cache_manager)

        logger.info("Services injected successfully")
