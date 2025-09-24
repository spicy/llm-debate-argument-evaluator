"""
CreateNodeCommand - Creates and evaluates new argument nodes.

This command handles the common logic for creating new argument nodes,
including evaluation, scoring, and adding to the tree state.
"""

from typing import Dict, Optional

from features.evaluation.evaluation_service import EvaluationService
from features.evaluation.score_aggregator_service import ScoreAggregatorService
from infrastructure.asynchronous.async_processing_service import AsyncProcessingService
from features.tree.multi_tree_state_service import MultiTreeStateService
from utils.logger import logger


class CreateNodeCommand:
    """
    Command for creating new argument nodes with evaluation and scoring.

    This command encapsulates the common pattern of:
    1. Evaluating an argument
    2. Aggregating scores
    3. Creating node data structure
    4. Adding to tree state service
    """

    def __init__(
        self,
        evaluation_service: EvaluationService,
        score_aggregator_service: ScoreAggregatorService,
        async_processing_service: AsyncProcessingService,
        tree_state_service: MultiTreeStateService,
    ):
        """Initialize the command with necessary services."""
        self.evaluation_service = evaluation_service
        self.score_aggregator_service = score_aggregator_service
        self.async_service = async_processing_service
        self.tree_state_service = tree_state_service

    async def execute(
        self,
        argument: str,
        arg_type: str,
        parent_node_id: Optional[int] = None,
        category: str = None,
        topic: str = None,
    ) -> Optional[Dict]:
        """
        Create a new argument node with evaluation and add it to the tree.

        Args:
            argument: The argument text
            arg_type: Type of argument (support, oppose, root, etc.)
            parent_node_id: ID of parent node (None for root nodes)
            category: Category for the argument (inherited from parent if not provided)
            topic: Topic for the argument (inherited from parent if not provided)

        Returns:
            Created node dictionary if successful, None otherwise
        """
        logger.debug(f"Creating new {arg_type} node: {argument[:50]}...")

        try:
            # Get parent node info if this isn't a root node
            parent_node = None
            if parent_node_id is not None:
                parent_node = self.tree_state_service.get_node(str(parent_node_id))
                if not parent_node:
                    logger.error(f"Parent node {parent_node_id} not found")
                    return None

            # Inherit category and topic from parent if not provided
            if parent_node:
                category = category or parent_node.get("category", "general")
                topic = topic or parent_node.get("topic", "Unknown")
                depth = parent_node.get("depth", 0) + 1
            else:
                # Root node defaults
                category = category or "general"
                topic = topic or "Unknown"
                depth = 0

            # Evaluate the argument
            evaluation_result = await self.evaluation_service.evaluate_argument(
                argument
            )
            scores = self.score_aggregator_service.aggregate_scores(evaluation_result)

            # Create node data structure
            new_node_data = {
                "argument": argument,
                "category": category,
                "topic": topic,
                "evaluation": scores,
                "parent_id": parent_node_id,
                "depth": depth,
                "argument_type": arg_type,
                "visits": 0,  # Initialize for UCB1 algorithm
                "wins": 0.0,  # Initialize for UCB1 algorithm
            }

            # Add to tree state service
            new_node = self.tree_state_service.add_node(new_node_data)

            if new_node:
                logger.info(
                    f"Created {arg_type} node ID {new_node['id']}: {argument[:50]}..."
                )
                # Queue for async evaluation updates
                await self.async_service.queue_evaluation(new_node)
                return new_node
            else:
                logger.error("Failed to add node to tree state service")
                return None

        except Exception as e:
            logger.error(f"Error creating node: {e}", exc_info=True)
            return None
