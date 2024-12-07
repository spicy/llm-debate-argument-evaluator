from config import memoization_config
from config.environment import environment_config
from evaluation.model_factory import ModelFactory
from evaluation.models.model_injector import ModelInjector
from memoization.cache_manager import CacheManager
from memoization.semantic_similarity import SemanticSimilarity
from services.argument_generation_service import ArgumentGenerationService
from services.async_processing_service import AsyncProcessingService
from services.evaluation_service import EvaluationService
from services.memoization_service import MemoizationService
from services.model_selection_service import ModelSelectionService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import logger


class ServicesInjector:
    @staticmethod
    def inject_services(registry):
        logger.debug("Injecting services")

        # Initialize core services
        model_factory = ModelFactory()
        registry.register("model_factory", model_factory)

        # Inject models into the factory
        logger.debug(f"Current enabled LLMs: {environment_config.ENABLED_LLMS}")
        ModelInjector.inject_models(model_factory)

        # Verify models were injected
        available_models = list(model_factory.get_models().keys())
        logger.debug(f"Available models after injection: {available_models}")

        if not available_models:
            logger.error("No models were successfully injected")
            raise ValueError("Failed to inject any LLM models")

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

        # Get the first available model for argument generation
        default_model = model_factory.get_models().get(
            list(model_factory.get_models().keys())[0]
        )
        argument_generation_service = ArgumentGenerationService(default_model)

        score_aggregator_service = ScoreAggregatorService()

        # Register services
        registry.register("async_processing_service", async_processing_service)
        registry.register("memoization_service", memoization_service)
        registry.register("evaluation_service", evaluation_service)
        registry.register("model_selection_service", model_selection_service)
        registry.register("argument_generation_service", argument_generation_service)
        registry.register("score_aggregator_service", score_aggregator_service)

        logger.info("Services injected successfully")
