from services.async_processing_service import AsyncProcessingService
from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class SubmitArgumentCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
        score_aggregator_service: ScoreAggregatorService,
        async_processing_service: AsyncProcessingService,
    ):
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service
        self.async_service = async_processing_service

    @log_execution_time
    async def execute(self, argument: str, category: str):
        logger.debug(f"Submitting and evaluating argument in category: {category}")

        # Evaluate the submitted argument asynchronously
        evaluation_task = await self.async_service.process_async(
            self.evaluation_service.evaluate_argument(argument)
        )

        evaluation_results = await evaluation_task
        evaluation_result = self.score_aggregator_service.average_scores(
            evaluation_results
        )

        logger.debug("Argument evaluation completed")

        # Create a new node with the argument and its evaluation
        new_node = {
            "id": self.priority_queue_service.get_unique_id(),
            "argument": argument,
            "category": category,
            "topic": "User Submitted",
            "subtopic": category,
            "evaluation": evaluation_result,
            "parent": -1,
        }

        # Queue the new node for evaluation
        await self.async_service.queue_evaluation(new_node)

        logger.debug("New node queued for evaluation")
