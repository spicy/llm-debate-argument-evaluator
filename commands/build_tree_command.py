"""
BuildTreeCommand - Builds out argument trees using MCTS traversal.

This command coordinates the tree building process by delegating to the
controller's expand_node method, which ensures proper auto-updates.
"""

from typing import Any, Dict, List, Callable, Awaitable

from features.tree.traversal_logic import TraversalLogic
from utils.logger import logger


class BuildTreeCommand:
    def __init__(
        self,
        traversal_logic: TraversalLogic,
        expand_node_func: Callable[[int], Awaitable[List[Dict]]] = None,
    ) -> None:
        """
        Initialize the command with traversal logic and expand function.

        Args:
            traversal_logic: Logic for MCTS traversal
            expand_node_func: Function to expand nodes (should be controller.expand_node)
        """
        self.traversal_logic: TraversalLogic = traversal_logic
        self.expand_node_func = expand_node_func

    async def execute(self, start_node_id: int, max_depth: int):
        """
        Build out the tree from a selected node using MCTS traversal.

        Args:
            start_node_id: ID of the selected node to build from
            max_depth: Maximum depth relative to the selected node
        """
        logger.info(f"Starting tree build from selected node: {start_node_id}")

        # Check if node exists using data service
        if not self.traversal_logic.data_service.get_node(start_node_id):
            logger.error(f"Selected node {start_node_id} does not exist")
            return

        # Use the provided expand function (should be controller.expand_node)
        expand_func = self.expand_node_func
        if not expand_func:
            logger.error("No expand function provided to BuildTreeCommand")
            return

        async for _ in self.traversal_logic.traverse(
            int(start_node_id),
            expand_node_func=expand_func,
            max_depth=max_depth,
        ):
            # This loop drives the generator-based traversal
            pass

        # After traversal, log the best path found
        self.traversal_logic.log_optimal_path()
