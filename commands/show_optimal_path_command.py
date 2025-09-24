"""
This module defines the command for showing the optimal path in the tree.
"""

from features.tree.multi_tree_state_service import MultiTreeStateService
from features.tree.traversal_logic import TraversalLogic
from utils.logger import logger


class ShowOptimalPathCommand:
    def __init__(
        self,
        tree_state_service: MultiTreeStateService,
        traversal_logic: TraversalLogic,
    ):
        """Initializes the command with the state service and traversal logic."""
        self.tree_state_service = tree_state_service
        self.traversal_logic = traversal_logic

    async def execute(self):
        """Calculates and stores the optimal path, triggering a UI update."""
        logger.info("Calculating and showing the optimal path...")
        optimal_path, best_score = self.traversal_logic.find_optimal_path()
        if optimal_path:
            await self.tree_state_service.set_optimal_path(optimal_path)
            self.traversal_logic.log_optimal_path(optimal_path, best_score)
        else:
            logger.info("No optimal path could be determined.")
