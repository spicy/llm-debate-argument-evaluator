from typing import Any, Dict

from commands.evaluate_debate_tree_command import EvaluateDebateTreeCommand
from commands.expand_node_command import ExpandNodeCommand
from debate_traversal.traversal_logic import TraversalLogic
from services.async_processing_service import AsyncProcessingService
from services.evaluation_service import EvaluationService
from services.interfaces.queue_service_interface import QueueServiceInterface
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class TraverseDebateCommand:
    def __init__(
        self,
        traversal_logic: TraversalLogic,
        priority_queue_service: QueueServiceInterface,
        expand_node_command: ExpandNodeCommand,
        evaluate_tree_command: EvaluateDebateTreeCommand,
        evaluation_service: EvaluationService,
        score_aggregator_service: ScoreAggregatorService,
        async_processing_service: AsyncProcessingService,
    ):
        self.traversal_logic = traversal_logic
        self.priority_queue_service = priority_queue_service
        self.expand_node_command = expand_node_command
        self.evaluate_tree_command = evaluate_tree_command
        self.evaluation_service = evaluation_service
        self.score_aggregator_service = score_aggregator_service
        self.async_service = async_processing_service

    @log_execution_time
    async def execute(self, root_node_id: str, max_depth: int) -> None:
        try:
            logger.info(f"Starting debate traversal from node: {root_node_id}")

            # Validate root node exists
            if not self._validate_node_exists(root_node_id):
                logger.error(f"Root node {root_node_id} does not exist")
                return

            async for node in self.traversal_logic.traverse(
                root_node_id,
                self.priority_queue_service.get_node,
                self._expand_node,
                self._evaluate_node,
                max_depth,
            ):
                # Queue the node for evaluation immediately after traversal
                await self.async_service.queue_evaluation(node)
                logger.debug(f"Traversed and queued node: {node['id']}")

            # Print the optimal path after traversal
            self.traversal_logic.print_optimal_path()

        except Exception as e:
            logger.error(f"Error during debate traversal: {str(e)}")
            raise

    async def _expand_node(self, node_id: str) -> list:
        """Expand a node and return its children"""
        # Process expansion asynchronously
        expansion_task = await self.async_service.process_async(
            self.expand_node_command.execute(node_id)
        )
        children = await expansion_task

        # Queue each child for evaluation
        for child in children:
            await self.async_service.queue_evaluation(child)

        return self.priority_queue_service.get_children(node_id)

    async def _evaluate_node(self, node_id: str) -> dict:
        """Evaluate a node and return its scores"""
        node = self.priority_queue_service.get_node(str(node_id))
        if not node:
            logger.warning(f"Node {node_id} not found during evaluation")
            return {}

        # Process evaluation asynchronously
        evaluation_task = await self.async_service.process_async(
            self.evaluation_service.evaluate_argument(node["argument"])
        )
        evaluation_result = await evaluation_task
        score = self.score_aggregator_service.average_scores(evaluation_result)

        # Create a copy of the node and update it
        updated_node = node.copy()
        updated_node["evaluation"] = score

        # Update node in priority queue
        self.priority_queue_service.update_node(node_id, updated_node)

        # Queue the node for traversal after evaluation
        await self.async_service.queue_traversal(node_id)

        logger.debug(f"Evaluation result for node {node_id}: {score}")
        return score

    def _validate_node_exists(self, node_id: str) -> bool:
        """Validate that a node exists in the priority queue"""
        return self.priority_queue_service.node_exists(str(node_id))
