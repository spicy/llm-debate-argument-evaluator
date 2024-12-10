from typing import Any, Dict

from commands.evaluate_debate_tree_command import EvaluateDebateTreeCommand
from commands.expand_node_command import ExpandNodeCommand
from debate_traversal.traversal_logic import TraversalLogic
from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class TraverseDebateCommand:
    def __init__(
        self,
        traversal_logic: TraversalLogic,
        priority_queue_service: PriorityQueueService,
        expand_node_command: ExpandNodeCommand,
        evaluate_tree_command: EvaluateDebateTreeCommand,
        evaluation_service: EvaluationService,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.traversal_logic = traversal_logic
        self.priority_queue_service = priority_queue_service
        self.expand_node_command = expand_node_command
        self.evaluate_tree_command = evaluate_tree_command
        self.evaluation_service = evaluation_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self, root_node_id: str, max_depth: int) -> None:
        try:
            logger.info(f"Starting debate traversal from node: {root_node_id}")

            async for node in self.traversal_logic.traverse(
                root_node_id,
                self.priority_queue_service.get_node,
                self._expand_node,
                self._evaluate_node,
                max_depth,
            ):
                logger.debug(f"Traversed node: {node['id']}")

            # Print the optimal path after traversal
            self.traversal_logic.print_optimal_path()

        except Exception as e:
            logger.error(f"Error during debate traversal: {str(e)}")
            raise

    async def _expand_node(self, node_id: str) -> list:
        """Expand a node and return its children"""
        await self.expand_node_command.execute(node_id)
        return self.priority_queue_service.get_children(node_id)

    async def _evaluate_node(self, node_id: str) -> dict:
        """Evaluate a node and return its scores"""
        node = self.priority_queue_service.get_node(str(node_id))
        if not node:
            logger.warning(f"Node {node_id} not found during evaluation")
            return {}

        # Evaluate only the specific node instead of the entire tree
        evaluation_result = await self.evaluation_service.evaluate_argument(
            node["argument"]
        )
        score = self.score_aggregator_service.average_scores(evaluation_result)

        # Create a copy of the node and update it
        updated_node = node.copy()
        updated_node["evaluation"] = score

        # Update node in priority queue with the same priority
        current_priority = updated_node.get("evaluation", "MEDIUM")
        self.priority_queue_service.update_node(node_id, updated_node)

        logger.debug(f"Evaluation result for node {node_id}: {score}")
        return score
