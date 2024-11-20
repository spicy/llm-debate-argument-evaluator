from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from utils.logger import log_execution_time, logger


class SubmitArgumentCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
    ):
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service

    @log_execution_time
    async def execute(self, argument: str, category: str):
        logger.debug(f"Submitting and evaluating argument in category: {category}")

        # Evaluate the submitted argument
        evaluation_result = await self.evaluation_service.evaluate_argument(argument)
        logger.debug("Argument evaluation completed")

        # Create a new node with the argument and its evaluation
        new_node = {
            "id": 1,  # Needed for priority queue (Should be unique, but for testing is 1)
            "argument": argument,
            "category": category,
            "evaluation": evaluation_result,
        }

        # Add the new node to the priority queue
        self.priority_queue_service.add_node(new_node)
        logger.debug("New node added to priority queue")

        logger.debug("Argument submitted and evaluated successfully.")
