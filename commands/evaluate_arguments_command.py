from services.evaluation_service import EvaluationService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class EvaluateArgumentsCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.evaluation_service = evaluation_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self, arguments: list):
        logger.debug(f"Evaluating {len(arguments)} arguments")
        evaluation_results = []

        for i, argument in enumerate(arguments):
            logger.debug(f"Evaluating argument {i + 1}")
            result = await self.evaluation_service.evaluate_argument(argument)
            evaluation_results.append(result)

        logger.debug("Aggregating scores from multiple models")
        aggregated_scores = self.score_aggregator_service.aggregate_scores(
            evaluation_results
        )

        for i, score in enumerate(aggregated_scores):
            logger.info(f"Argument {i + 1} aggregated score: {score}")

        return aggregated_scores
