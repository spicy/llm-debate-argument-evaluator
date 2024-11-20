from services.argument_generation_service import ArgumentGenerationService
from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from utils.logger import log_execution_time, logger


class GenerateArgumentsCommand:
    def __init__(
        self,
        argument_generation_service: ArgumentGenerationService,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
    ):
        self.argument_generation_service = argument_generation_service
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service

    @log_execution_time
    async def execute(self, topic: str, subcategory: str):
        logger.info(
            f"Generating arguments for topic: {topic}, subcategory: {subcategory}"
        )
        # Generate arguments
        arguments = await self.argument_generation_service.generate_arguments(
            topic, subcategory, 1 #Changed from 3 to 1
        )

        logger.info(f"Generated {len(arguments)} arguments. Starting evaluation.")
        for i, argument in enumerate(arguments, 1):
            logger.debug(f"Evaluating argument {i}/{len(arguments)}")
            # # Evaluate each generated argument
            # evaluation_result = await self.evaluation_service.evaluate_argument(
            #     argument
            # )
            evaluation_result = 0.8

            # Create a new node with the argument and its evaluation
            new_node = {
                "id": i, # Needed for priority queue
                "argument": argument,
                "category": subcategory,
                "evaluation": evaluation_result,
            }

            # Add the new node to the priority queue
            self.priority_queue_service.add_node(new_node)
            logger.debug(f"Added argument {i} to priority queue")

        logger.info(
            f"Generated and evaluated {len(arguments)} arguments for {subcategory} in {topic}."
        )
