"""
SubmitArgumentCommand - Submit user-provided arguments to the tree.

This command allows users to manually add arguments to the debate tree
by reusing the common node creation logic.
"""

from typing import Dict, Optional

from commands.create_node_command import CreateNodeCommand
from features.tree.multi_tree_state_service import MultiTreeStateService
from utils.logger import logger


class SubmitArgumentCommand:
    def __init__(
        self,
        create_node_command: CreateNodeCommand,
        tree_state_service: MultiTreeStateService,
    ):
        """Initialize the command with node creation logic."""
        self.create_node_command = create_node_command
        self.tree_state_service = tree_state_service

    async def execute(
        self, parent_node_id: int, argument: str, arg_type: str
    ) -> Optional[Dict]:
        """
        Submit a new user argument to the tree.

        Args:
            parent_node_id: ID of the parent node to attach to
            argument: The argument text
            arg_type: Type of argument (support, oppose, etc.)

        Returns:
            Created node if successful, None otherwise
        """
        logger.info(
            f"Submitting new {arg_type} argument for parent node {parent_node_id}"
        )

        # Validate parent node exists
        if not self.tree_state_service.get_node(str(parent_node_id)):
            logger.error(f"Parent node {parent_node_id} not found")
            return None

        # Use the shared node creation logic
        new_node = await self.create_node_command.execute(
            argument=argument, arg_type=arg_type, parent_node_id=parent_node_id
        )

        if new_node:
            logger.info(
                f"Successfully submitted argument with node ID: {new_node['id']}"
            )
        else:
            logger.error("Failed to submit argument")

        return new_node
