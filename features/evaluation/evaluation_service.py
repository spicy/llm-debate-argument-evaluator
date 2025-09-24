"""
TODO: This module...
"""

import asyncio
from config import evaluation_config
from features.evaluation.model_factory import ModelFactory
from infrastructure.caching.memoization_service import MemoizationService
from utils.logger import log_execution_time, logger


class EvaluationService:
    def __init__(
        self, model_factory: ModelFactory, memoization_service: MemoizationService
    ):
        self.model_factory = model_factory
        self.memoization_service = memoization_service
        self.evaluation_criteria = [
            evaluation_config.COHERENCE,
            evaluation_config.PERSUASION,
            evaluation_config.CULTURAL_ACCEPTANCE,
            evaluation_config.FACTUAL_ACCURACY,
        ]
        logger.info("EvaluationService initialized")

    @log_execution_time
    async def evaluate_argument(self, argument: str):
        """TODO: Add Simple Docstring"""
        logger.info(f"Evaluating argument: {argument[:50]}...")
        models = self.model_factory.get_models()
        model_names = list(models.keys())

        # Check for cached evaluation
        cached_evaluation = await self.memoization_service.get_cached_evaluation(
            argument, model_names
        )
        if cached_evaluation:
            logger.info(f"Using cached evaluation for: {argument[:50]}...")
            return cached_evaluation

        tasks = {}

        for model_name, model in models.items():
            logger.debug(f"Creating evaluation tasks for model: {model_name}")
            tasks[model_name] = {
                criterion: asyncio.create_task(
                    getattr(model, f"evaluate_{criterion}")(argument)
                )
                for criterion in self.evaluation_criteria
            }

        evaluations = {}
        for model_name, model_tasks in tasks.items():
            logger.debug(f"Awaiting tasks for model: {model_name}")

            results = await asyncio.gather(
                *model_tasks.values(), return_exceptions=True
            )

            evaluations[model_name] = {}
            for criterion, result in zip(model_tasks.keys(), results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Error evaluating {criterion} for {model_name}: {result}"
                    )
                    # Exclude this model's score for this criterion by not adding it
                else:
                    evaluations[model_name][criterion] = result

            if not evaluations[model_name]:
                # If a model failed on all criteria, remove it from the results
                del evaluations[model_name]
                logger.warning(
                    f"Model {model_name} failed on all evaluation criteria and will be excluded."
                )
            else:
                logger.info(
                    f"Evaluation results for {model_name}: {evaluations[model_name]}"
                )

        # Cache the new evaluation
        await self.memoization_service.cache_evaluation(
            argument, model_names, evaluations
        )

        logger.info("Argument evaluation completed")
        return evaluations
