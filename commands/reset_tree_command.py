"""
This module defines the command for resetting the currently selected tree.
"""

from features.tree.multi_tree_state_service import MultiTreeStateService
from utils.logger import logger


class ResetTreeCommand:
    def __init__(self, tree_state_service: MultiTreeStateService):
        """
        Initialize the command with a multi-tree state service.

        Args:
            tree_state_service: Multi-tree state service
        """
        self.tree_state_service = tree_state_service

    async def execute(self):
        """
        Reset the currently selected tree, clearing all its nodes.

        This will clear all nodes from the current tree but keep the tree
        metadata intact. The tree will be empty and ready for new content.
        """
        if not self.tree_state_service.has_current_tree:
            logger.warning("No tree currently selected for reset.")
            return

        current_tree = self.tree_state_service.current_tree
        logger.info(f"Resetting tree: {current_tree.display_name}")

        try:
            await self.tree_state_service.reset_current_tree()
            logger.info(f"Tree '{current_tree.name}' reset successfully.")
        except Exception as e:
            logger.error(f"An error occurred during tree reset: {e}", exc_info=True)
