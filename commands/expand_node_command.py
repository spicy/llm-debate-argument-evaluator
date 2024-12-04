from commands.generate_debate_arguments_command import GenerateDebateArgumentsCommand
from config import debate_tree_config  # MAX_CHILDREN_PER_NODE, MAX_TREE_DEPTH
from services.argument_generation_service import ArgumentGenerationService
from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class ExpandNodeCommand:
    def __init__(
        self,
        generate_debate_arguments_command: GenerateDebateArgumentsCommand,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.generate_debate_arguments_command = generate_debate_arguments_command
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self, node_id: str):
        logger.debug(f"Attempting to expand node with ID {node_id}")
        node = self.priority_queue_service.get_node(int(node_id))
        if not node:
            logger.warning(f"Node with ID {node_id} not found.")
            return

        # Generate arguments using the dedicated command
        arguments = await self.generate_debate_arguments_command.execute(
            node["argument"], node["category"]
        )

        logger.info(f"Generated {len(arguments)} arguments. Starting evaluation.")
        for i, argument in enumerate(arguments, 1):
            evaluation_results = await self.evaluation_service.evaluate_argument(
                argument
            )
            evaluation_result = self.score_aggregator_service.average_scores(
                evaluation_results
            )

            new_node = {
                "id": self.priority_queue_service.get_unique_id(),
                "argument": argument,
                "category": node["category"],
                "topic": node.get("topic", "Unknown"),
                "subtopic": node.get("subtopic", node["category"]),
                "evaluation": evaluation_result,
                "parent": node["id"],
                "depth": node.get("depth", 0) + 1,
            }

            self.priority_queue_service.add_node(new_node)
            logger.debug(f"Added argument {i} to priority queue")
