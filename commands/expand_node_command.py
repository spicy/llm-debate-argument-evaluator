from config import debate_tree_config  # MAX_CHILDREN_PER_NODE, MAX_TREE_DEPTH
from services.argument_generation_service import ArgumentGenerationService
from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class ExpandNodeCommand:
    def __init__(
        self,
        argument_generation_service: ArgumentGenerationService,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.argument_generation_service = argument_generation_service
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self, node_id: str):
        logger.debug(f"Attempting to expand node with ID {node_id}")
        # Retrieve the node from the priority queue
        if node_id == "top": 
            node = self.priority_queue_service.get_top_node()[2]
        else:
            node = self.priority_queue_service.get_node(int(node_id))
        logger.debug(f"Node: {node}")
        if not node:
            logger.warning(f"Node with ID {node_id} not found.")
            return

        category = node["category"]
        support = f"Based on this argument: {node["argument"]}, make an argument that supports it further."
        against = f"Based on this argument: {node["argument"]}, make an argument that rebuttals this argument."
        # Expand the node like it was before in the generation arguments "make 3 more arguments that support this" and "make 3 more arguments that are against this"
        arguments = await self.argument_generation_service.generate_arguments(
            "none", category, support, against, 1
        )  # For now 1 from 3

        logger.info(f"Generated {len(arguments)} arguments. Starting evaluation.")
        for i, argument in enumerate(arguments, 1):
            logger.debug(f"Evaluating argument {i}/{len(arguments)}")
            # Evaluate each generated argument
            evaluation_results = await self.evaluation_service.evaluate_argument(
                argument
            )
            evaluation_result = self.score_aggregator_service.average_scores(
                evaluation_results
            )

            new_node = {
                "id": self.priority_queue_service.get_unique_id(),
                "argument": argument,
                "category": category,
                "evaluation": evaluation_result,
                "parent": node["id"],
            }

            self.priority_queue_service.add_node(new_node)
            logger.debug(f"Added argument {i} to priority queue")

        # Expand the node in the debate tree
        # expanded_nodes = await self.node_expansion_handler.expand_node(node)

        logger.info(
            f"Node {node_id} expanded successfully. Added {len(arguments)} new nodes."
        )
