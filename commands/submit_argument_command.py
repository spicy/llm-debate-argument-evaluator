from services.evaluation_service import EvaluationService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger
from visualization.priority_queue_service import PriorityQueueService


class SubmitArgumentCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self, argument: str, category: str):
        logger.debug(f"Submitting and evaluating argument in category: {category}")

        # Evaluate the submitted argument

        evaluation_results = await self.evaluation_service.evaluate_argument(argument)
        evaluation_result = self.score_aggregator_service.average_scores(
            evaluation_results
        )
        # evaluation_result = 0.5

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

        # Add the new node to the priority queue
        self.priority_queue_service.add_node(new_node)
        logger.debug("New node added to priority queue")

        logger.debug("Argument submitted and evaluated successfully.")
