"""
TODO: This module...
"""

from typing import Dict, List, Optional

from commands.generate_tree_arguments_command import GenerateTreeArgumentsCommand
from commands.create_node_command import CreateNodeCommand
from features.tree.multi_tree_state_service import MultiTreeStateService
from config import tree_config
from utils.logger import logger


class ExpandNodeCommand:
    def __init__(
        self,
        generate_tree_arguments_command: GenerateTreeArgumentsCommand,
        create_node_command: CreateNodeCommand,
        tree_state_service: MultiTreeStateService,
    ):
        """Initialize the command with argument generation and node creation logic."""
        self.generate_tree_arguments_command = generate_tree_arguments_command
        self.create_node_command = create_node_command
        self.tree_state_service = tree_state_service

    async def execute(self, node_id: int) -> List[Dict]:
        """Expands a node by generating and adding child arguments"""
        logger.debug(f"Attempting to expand node with ID {node_id}")

        # Get current tree ID from tree state service
        if not self.tree_state_service.has_current_tree:
            logger.error("No tree currently selected. Cannot expand node.")
            return []

        node = self.tree_state_service.get_node(str(node_id))
        if not node:
            logger.error(f"Cannot expand non-existent node: {node_id}")
            return []

        existing_children = self.tree_state_service.get_children(str(node_id))
        if len(existing_children) >= tree_config.MAX_CHILDREN_PER_NODE:
            logger.warning(f"Node {node_id} already has maximum children")
            return existing_children

        try:
            argument_data = await self.generate_tree_arguments_command.execute(
                node["argument"],
                node.get("topic"),
                node.get("category"),
                tree_config.MAX_CHILDREN_PER_NODE,
            )

            new_nodes = []
            for arg_info in argument_data:
                # Use the shared node creation logic
                child_node = await self.create_node_command.execute(
                    argument=arg_info["text"],
                    arg_type=arg_info["type"],
                    parent_node_id=node["id"],
                )
                if child_node:
                    new_nodes.append(child_node)

            logger.info(f"Expanded node {node_id} with {len(new_nodes)} new children")
            return new_nodes

        except Exception as e:
            logger.error(f"Error expanding node {node_id}: {str(e)}")
            return []
