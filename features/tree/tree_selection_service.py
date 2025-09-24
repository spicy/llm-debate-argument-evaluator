"""
TreeSelectionService - Utility for handling tree selection and switching.
"""

from typing import List, Optional
from uuid import UUID

from features.tree.models.tree import Tree
from features.tree.multi_tree_state_service import MultiTreeStateService
from utils.logger import logger


class TreeSelectionService:
    """
    Service for handling tree selection logic and user interactions.

    This service provides utilities for:
    - Selecting trees from available options
    - Handling tree switching with proper validation
    - Providing formatted tree information for UI
    """

    def __init__(self, multi_tree_state_service: MultiTreeStateService):
        """
        Initialize with the multi-tree state service.

        Args:
            multi_tree_state_service: Service managing multiple trees
        """
        self.state_service = multi_tree_state_service

    def get_available_trees_info(self) -> List[dict]:
        """
        Get formatted information about available trees for display.

        Returns:
            List of dictionaries containing tree display information
        """
        trees = self.state_service.get_available_trees()
        tree_info = []

        for tree in trees:
            # Get node count for this tree (requires switching temporarily or querying)
            try:
                node_count = self.state_service.repository.get_node_count(tree.id)
            except Exception as e:
                logger.warning(f"Could not get node count for tree {tree.id}: {e}")
                node_count = 0

            info = {
                "id": tree.id,
                "name": tree.name,
                "topic": tree.topic,
                "description": tree.description or "No description",
                "node_count": node_count,
                "created_at": tree.created_at,
                "display_name": tree.display_name,
                "is_current": (
                    self.state_service.current_tree_id == tree.id
                    if self.state_service.has_current_tree
                    else False
                ),
            }
            tree_info.append(info)

        return tree_info

    def get_tree_selection_prompt(self) -> str:
        """
        Generate a formatted prompt showing available trees for selection.

        Returns:
            Formatted string with tree options
        """
        trees_info = self.get_available_trees_info()

        if not trees_info:
            return "No trees available. Create a new tree to get started."

        prompt = "Available trees:\n"
        for i, tree_info in enumerate(trees_info, 1):
            current_marker = " (CURRENT)" if tree_info["is_current"] else ""
            prompt += (
                f"  {i}. {tree_info['display_name']}{current_marker}\n"
                f"     Description: {tree_info['description']}\n"
                f"     Nodes: {tree_info['node_count']} | "
                f"Created: {tree_info['created_at'].strftime('%Y-%m-%d %H:%M') if tree_info['created_at'] else 'Unknown'}\n"
            )

        return prompt

    async def select_tree_by_index(self, index: int) -> bool:
        """
        Select a tree by its index in the available trees list.

        Args:
            index: 1-based index of the tree to select

        Returns:
            True if selection was successful, False otherwise
        """
        trees = self.state_service.get_available_trees()

        if not trees:
            logger.error("No trees available to select")
            return False

        if index < 1 or index > len(trees):
            logger.error(
                f"Invalid tree index: {index}. Must be between 1 and {len(trees)}"
            )
            return False

        selected_tree = trees[index - 1]
        return await self.state_service.switch_to_tree(selected_tree.id)

    async def select_tree_by_name(self, name: str) -> bool:
        """
        Select a tree by its name.

        Args:
            name: Name of the tree to select

        Returns:
            True if selection was successful, False otherwise
        """
        trees = self.state_service.get_available_trees()

        for tree in trees:
            if tree.name.lower() == name.lower():
                return await self.state_service.switch_to_tree(tree.id)

        logger.error(f"Tree with name '{name}' not found")
        return False

    async def select_tree_by_id(self, tree_id: UUID) -> bool:
        """
        Select a tree by its UUID.

        Args:
            tree_id: UUID of the tree to select

        Returns:
            True if selection was successful, False otherwise
        """
        return await self.state_service.switch_to_tree(tree_id)

    def get_current_tree_summary(self) -> Optional[str]:
        """
        Get a summary of the currently selected tree.

        Returns:
            Formatted string with current tree information, or None if no tree selected
        """
        if not self.state_service.has_current_tree:
            return None

        tree = self.state_service.current_tree
        node_count = len(self.state_service.get_all_nodes())

        return (
            f"Current Tree: {tree.display_name}\n"
            f"Description: {tree.description or 'No description'}\n"
            f"Nodes: {node_count}\n"
            f"Created: {tree.created_at.strftime('%Y-%m-%d %H:%M') if tree.created_at else 'Unknown'}"
        )

    async def ensure_tree_selected(self) -> bool:
        """
        Ensure a tree is selected, automatically selecting the first available if none is selected.

        Returns:
            True if a tree is selected (or was successfully auto-selected), False otherwise
        """
        if self.state_service.has_current_tree:
            return True

        # Try to auto-select the first available tree
        trees = self.state_service.get_available_trees()
        if trees:
            logger.info(f"Auto-selecting first available tree: {trees[0].display_name}")
            return await self.state_service.switch_to_tree(trees[0].id)

        logger.warning("No trees available for auto-selection")
        return False

    def validate_tree_name(self, name: str) -> tuple[bool, str]:
        """
        Validate a tree name for creation.

        Args:
            name: Name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Tree name cannot be empty"

        if len(name.strip()) < 3:
            return False, "Tree name must be at least 3 characters long"

        if len(name.strip()) > 100:
            return False, "Tree name must be less than 100 characters"

        # Check if name already exists
        if self.state_service.tree_metadata_repository.name_exists(name.strip()):
            return False, f"Tree with name '{name.strip()}' already exists"

        return True, ""

    async def create_and_switch_to_new_tree(
        self, name: str, topic: str, description: str = None
    ) -> bool:
        """
        Create a new tree and automatically switch to it.

        Args:
            name: Name for the new tree
            topic: Topic for the new tree
            description: Optional description

        Returns:
            True if creation and switch were successful, False otherwise
        """
        # Validate name
        is_valid, error_msg = self.validate_tree_name(name)
        if not is_valid:
            logger.error(f"Invalid tree name: {error_msg}")
            return False

        # Create the tree
        new_tree = await self.state_service.create_new_tree(
            name.strip(), topic.strip(), description.strip() if description else None
        )

        if new_tree:
            # Switch to the new tree
            success = await self.state_service.switch_to_tree(new_tree.id)
            if success:
                logger.info(
                    f"Created and switched to new tree: {new_tree.display_name}"
                )
                return True
            else:
                logger.error(
                    f"Created tree but failed to switch to it: {new_tree.display_name}"
                )
                return False

        logger.error(f"Failed to create tree: {name}")
        return False
