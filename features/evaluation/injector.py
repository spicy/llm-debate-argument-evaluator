"""
TODO: This module...
"""

from features.evaluation.api_clients import (
    ChatGPTAPIClient,
    ClaudeAPIClient,
    GoogleAPIClient,
    GrokAPIClient,
)
from features.evaluation.evaluation_service import EvaluationService
from features.evaluation.model_factory import ModelFactory
from features.evaluation.model_selection_service import ModelSelectionService
from features.evaluation.models import (
    ChatGPTModel,
    ClaudeModel,
    GoogleModel,
    GrokModel,
    ModelInjector,
)
from features.evaluation.score_aggregator import ScoreAggregator
from features.evaluation.score_aggregator_service import ScoreAggregatorService
from utils.dependency_registry import DependencyRegistry
from utils.logger import logger


class EvaluationInjector:
    def __init__(self, registry: DependencyRegistry):
        """TODO: Add Simple Docstring"""
        self.registry = registry

    def inject(self):
        """TODO: Add Simple Docstring"""
        logger.debug("Injecting evaluation components")

        model_factory = ModelFactory()
        self.registry.register("model_factory", model_factory)

        model_injector = ModelInjector(model_factory)
        model_injector.inject_models()

        score_aggregator = ScoreAggregator()
        self.registry.register("score_aggregator", score_aggregator)

        evaluation_service = EvaluationService(
            model_factory=model_factory,
            memoization_service=self.registry.get("memoization_service"),
        )
        self.registry.register("evaluation_service", evaluation_service)

        score_aggregator_service = ScoreAggregatorService(
            score_aggregator=score_aggregator
        )
        self.registry.register("score_aggregator_service", score_aggregator_service)

        model_selection_service = ModelSelectionService(model_factory.get_models())
        self.registry.register("model_selection_service", model_selection_service)

        logger.info("Evaluation components injected successfully")
