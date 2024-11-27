from services.evaluation_service import EvaluationService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import logger

from .model_factory import ModelFactory
from .models.model_injector import ModelInjector


class EvaluationInjector:
    @staticmethod
    def inject_evaluation_services(registry):
        logger.debug("Injecting evaluation services")

        model_factory = ModelFactory()
        registry.register("model_factory", model_factory)

        ModelInjector.inject_models(model_factory)

        evaluation_service = EvaluationService(model_factory)
        score_aggregator_service = ScoreAggregatorService()

        registry.register("evaluation_service", evaluation_service)
        registry.register("score_aggregator_service", score_aggregator_service)

        logger.info("Evaluation services injected successfully")
