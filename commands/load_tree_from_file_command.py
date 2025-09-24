"""
This module defines the command for loading tree nodes from a file.
"""

import json

from features.tree.multi_tree_state_service import MultiTreeStateService
from utils.logger import logger


class LoadTreeFromFileCommand:
    def __init__(self, tree_state_service: MultiTreeStateService):
        """
        Initialize the command with a multi-tree state service.

        Args:
            tree_state_service: Multi-tree state service
        """
        self.tree_state_service = tree_state_service

    async def execute(self, file_path: str):
        """
        Load nodes from a JSON file into the currently selected tree.

        Args:
            file_path: Path to the JSON file containing node data
        """
        if not self.tree_state_service.has_current_tree:
            logger.error("No tree currently selected. Cannot load nodes from file.")
            return

        current_tree = self.tree_state_service.current_tree
        logger.info(
            f"Loading nodes from {file_path} into tree: {current_tree.display_name}"
        )

        try:
            with open(file_path, "r") as f:
                nodes_data = json.load(f)

            if not isinstance(nodes_data, list):
                logger.error("Invalid file format. Expected a list of nodes.")
                return

            node_count = 0
            for node_data in nodes_data:
                # We let the database handle the ID generation
                node_data.pop("id", None)

                # Remove tree_id if present in file data - will be set by current tree
                node_data.pop("tree_id", None)

                new_node = self.tree_state_service.add_node(node_data)
                if new_node:
                    node_count += 1

            logger.info(
                f"Successfully loaded and created {node_count} nodes in tree '{current_tree.name}'."
            )

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in {file_path}")
        except Exception as e:
            logger.error(f"Error loading file: {e}", exc_info=True)
