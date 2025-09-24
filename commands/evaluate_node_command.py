"""
TODO: This module...
"""

from features.evaluation.evaluation_service import EvaluationService
from features.evaluation.score_aggregator_service import ScoreAggregatorService
from features.tree.multi_tree_state_service import MultiTreeStateService
from utils.logger import logger


class EvaluateNodeCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        score_aggregator_service: ScoreAggregatorService,
        state_service: MultiTreeStateService,
    ):
        """Initializes the command with necessary services."""
        self.evaluation_service = evaluation_service
        self.score_aggregator_service = score_aggregator_service
        self.state_service = state_service

    async def execute(self, node_id: int):
        """Evaluates a node, updates the database, and then updates the in-memory state."""
        logger.info(f"Evaluating single node: {node_id}")

        # Get current tree ID from state service
        if not self.state_service.has_current_tree:
            logger.error("No tree currently selected. Cannot evaluate node.")
            return

        node = self.state_service.get_node(str(node_id))
        if not node:
            logger.error(f"Node {node_id} not found for evaluation")
            return

        # Skip evaluation for root nodes as they represent topics, not arguments
        if node.get("argument_type") == "root":
            logger.info(
                f"Skipping evaluation for root node {node_id} (topic: {node.get('argument', 'Unknown')})"
            )
            return

        try:
            evaluation_results = await self.evaluation_service.evaluate_argument(
                node["argument"]
            )
            aggregated_scores = self.score_aggregator_service.aggregate_scores(
                evaluation_results
            )

            await self.state_service.update_node(
                str(node_id), {"evaluation": aggregated_scores}
            )
            logger.info(f"Completed evaluation of node {node_id}")

        except Exception as e:
            logger.error(f"Error evaluating node {node_id}: {e}", exc_info=True)
