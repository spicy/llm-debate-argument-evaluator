"""
SwitchTreeCommand - Switch between different debate trees.
"""

from typing import Optional
from uuid import UUID

from features.tree.tree_selection_service import TreeSelectionService
from utils.logger import logger


class SwitchTreeCommand:
    """
    Command for switching between different debate trees.

    This command allows users to switch their current working tree
    by name, index, or UUID.
    """

    def __init__(self, tree_selection_service: TreeSelectionService):
        """
        Initialize the command with tree selection service.

        Args:
            tree_selection_service: Service for tree selection and management
        """
        self.tree_selection_service = tree_selection_service

    async def execute_by_name(self, name: str) -> bool:
        """
        Switch to a tree by its name.

        Args:
            name: Name of the tree to switch to

        Returns:
            True if switch was successful, False otherwise
        """
        if not name or not name.strip():
            logger.error("Tree name cannot be empty")
            return False

        logger.info(f"Switching to tree by name: '{name}'")

        try:
            success = await self.tree_selection_service.select_tree_by_name(
                name.strip()
            )

            if success:
                current_summary = self.tree_selection_service.get_current_tree_summary()
                logger.info(f"Successfully switched to tree: '{name}'")
                if current_summary:
                    logger.info(f"Tree details:\n{current_summary}")
                return True
            else:
                logger.error(f"Failed to switch to tree: '{name}'")
                return False

        except Exception as e:
            logger.error(f"Error switching to tree '{name}': {e}")
            return False

    async def execute_by_index(self, index: int) -> bool:
        """
        Switch to a tree by its index in the available trees list.

        Args:
            index: 1-based index of the tree to switch to

        Returns:
            True if switch was successful, False otherwise
        """
        logger.info(f"Switching to tree by index: {index}")

        try:
            success = await self.tree_selection_service.select_tree_by_index(index)

            if success:
                current_summary = self.tree_selection_service.get_current_tree_summary()
                logger.info(f"Successfully switched to tree at index {index}")
                if current_summary:
                    logger.info(f"Tree details:\n{current_summary}")
                return True
            else:
                logger.error(f"Failed to switch to tree at index {index}")
                return False

        except Exception as e:
            logger.error(f"Error switching to tree at index {index}: {e}")
            return False

    async def execute_by_id(self, tree_id: UUID) -> bool:
        """
        Switch to a tree by its UUID.

        Args:
            tree_id: UUID of the tree to switch to

        Returns:
            True if switch was successful, False otherwise
        """
        logger.info(f"Switching to tree by ID: {tree_id}")

        try:
            success = await self.tree_selection_service.select_tree_by_id(tree_id)

            if success:
                current_summary = self.tree_selection_service.get_current_tree_summary()
                logger.info(f"Successfully switched to tree: {tree_id}")
                if current_summary:
                    logger.info(f"Tree details:\n{current_summary}")
                return True
            else:
                logger.error(f"Failed to switch to tree: {tree_id}")
                return False

        except Exception as e:
            logger.error(f"Error switching to tree {tree_id}: {e}")
            return False

    async def execute_interactive(self) -> bool:
        """
        Execute the command with interactive tree selection.

        Shows available trees and prompts user to select one.

        Returns:
            True if switch was successful, False otherwise
        """
        try:
            # Show available trees
            trees_prompt = self.tree_selection_service.get_tree_selection_prompt()
            print("\n" + trees_prompt)

            # Get user selection
            choice = input(
                "\nEnter tree number to switch to (or 'cancel' to abort): "
            ).strip()

            if choice.lower() in ["cancel", "c", "quit", "q"]:
                logger.info("Tree switch cancelled by user")
                return False

            # Try to parse as index
            try:
                index = int(choice)
                return await self.execute_by_index(index)
            except ValueError:
                logger.error("Invalid selection. Please enter a number.")
                return False

        except KeyboardInterrupt:
            logger.info("Tree switch cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Error during interactive tree switch: {e}")
            return False

    def show_current_tree(self) -> Optional[str]:
        """
        Show information about the currently selected tree.

        Returns:
            Current tree summary string if a tree is selected, None otherwise
        """
        current_summary = self.tree_selection_service.get_current_tree_summary()

        if current_summary:
            logger.info("Current tree information:")
            logger.info(current_summary)
            return current_summary
        else:
            logger.info("No tree currently selected")
            return None

    async def ensure_tree_selected(self) -> bool:
        """
        Ensure a tree is selected, auto-selecting if none is current.

        Returns:
            True if a tree is selected, False if no trees are available
        """
        return await self.tree_selection_service.ensure_tree_selected()
