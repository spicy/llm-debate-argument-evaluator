"""
This module defines the command for creating the root node of a tree.
"""

from features.tree.multi_tree_state_service import MultiTreeStateService
from features.tree.tree_metadata_repository import TreeMetadataRepository
from utils.logger import logger


class CreateRootNodeCommand:
    def __init__(
        self,
        tree_state_service: MultiTreeStateService,
        tree_metadata_repository: TreeMetadataRepository,
    ):
        """
        Initialize the command with tree services.

        Args:
            tree_state_service: Multi-tree state service for node operations
            tree_metadata_repository: Repository for tree metadata operations
        """
        self.tree_state_service = tree_state_service
        self.tree_metadata_repository = tree_metadata_repository

    async def execute(self, topic: str) -> str | None:
        """
        Create a root node and add it to the current tree.

        Args:
            topic: The topic for the root node

        Returns:
            Node ID if successful, None otherwise
        """
        # Ensure a tree is currently selected
        if not self.tree_state_service.has_current_tree:
            logger.error("No tree currently selected. Cannot create root node.")
            return None

        current_tree = self.tree_state_service.current_tree
        logger.info(
            f"Creating root node for topic '{topic}' in tree: {current_tree.display_name}"
        )

        node_data = {
            "argument": topic,
            "category": topic,
            "topic": topic,
            "parent_id": None,
            "depth": 0,
            "argument_type": "root",
            "visits": 1,  # Initialize visits for UCB1
            "wins": 0,  # Initialize wins for UCB1
        }

        new_node = self.tree_state_service.add_node(node_data)

        if new_node:
            node_id = new_node["id"]
            logger.info(f"Created root node with ID: {node_id}")

            # Update tree metadata to reference the root node
            await self._update_tree_root_reference(node_id)

            return str(node_id)
        else:
            logger.error("Failed to create root node.")
            return None

    async def _update_tree_root_reference(self, root_node_id: int):
        """
        Update the tree metadata to reference the new root node.

        Args:
            root_node_id: ID of the newly created root node
        """
        try:
            tree_id = self.tree_state_service.current_tree_id
            updated_tree = self.tree_metadata_repository.update_tree(
                tree_id, {"root_node_id": root_node_id}
            )

            if updated_tree:
                logger.debug(
                    f"Updated tree {tree_id} root node reference to {root_node_id}"
                )
                # Update the current tree object in the state service
                self.tree_state_service.current_tree = updated_tree
            else:
                logger.warning(f"Failed to update tree {tree_id} root node reference")

        except Exception as e:
            logger.error(f"Error updating tree root reference: {e}")
