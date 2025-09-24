"""
ListTreesCommand - Display available debate trees with detailed information.
"""

from features.tree.tree_selection_service import TreeSelectionService
from utils.logger import logger


class ListTreesCommand:
    """
    Command for listing all available debate trees.

    This command displays comprehensive information about all trees
    including their metadata, node counts, and current status.
    """

    def __init__(self, tree_selection_service: TreeSelectionService):
        """
        Initialize the command with tree selection service.

        Args:
            tree_selection_service: Service for tree selection and management
        """
        self.tree_selection_service = tree_selection_service

    async def execute(self, detailed: bool = True) -> bool:
        """
        List all available trees with optional detailed information.

        Args:
            detailed: Whether to show detailed information for each tree

        Returns:
            True if listing was successful, False otherwise
        """
        logger.info("Retrieving list of available trees...")

        try:
            trees_info = self.tree_selection_service.get_available_trees_info()

            if not trees_info:
                logger.info("No trees found. Create a new tree to get started.")
                return True

            # Display tree information
            if detailed:
                self._display_detailed_trees(trees_info)
            else:
                self._display_simple_trees(trees_info)

            # Show current tree status
            current_summary = self.tree_selection_service.get_current_tree_summary()
            if current_summary:
                logger.info(f"\n--- Current Tree ---")
                logger.info(current_summary)
            else:
                logger.info("\nNo tree currently selected.")

            return True

        except Exception as e:
            logger.error(f"Error listing trees: {e}")
            return False

    def _display_detailed_trees(self, trees_info: list):
        """
        Display detailed information about all trees.

        Args:
            trees_info: List of tree information dictionaries
        """
        logger.info(f"\n--- Available Trees ({len(trees_info)} total) ---")

        for i, tree_info in enumerate(trees_info, 1):
            current_marker = " ← CURRENT" if tree_info["is_current"] else ""

            logger.info(f"\n{i}. {tree_info['display_name']}{current_marker}")
            logger.info(f"   ID: {tree_info['id']}")
            logger.info(f"   Topic: {tree_info['topic']}")
            logger.info(f"   Description: {tree_info['description']}")
            logger.info(f"   Nodes: {tree_info['node_count']}")

            if tree_info["created_at"]:
                created_str = tree_info["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"   Created: {created_str}")
            else:
                logger.info(f"   Created: Unknown")

        logger.info("-" * 50)

    def _display_simple_trees(self, trees_info: list):
        """
        Display simple list of trees.

        Args:
            trees_info: List of tree information dictionaries
        """
        logger.info(f"\n--- Available Trees ({len(trees_info)} total) ---")

        for i, tree_info in enumerate(trees_info, 1):
            current_marker = " ← CURRENT" if tree_info["is_current"] else ""
            node_count = tree_info["node_count"]

            logger.info(
                f"{i:2}. {tree_info['name']:<30} "
                f"({node_count:3} nodes){current_marker}"
            )

        logger.info("-" * 50)

    async def execute_with_stats(self) -> bool:
        """
        Execute the command with additional statistics.

        Returns:
            True if listing was successful, False otherwise
        """
        try:
            trees_info = self.tree_selection_service.get_available_trees_info()

            if not trees_info:
                logger.info("No trees found. Create a new tree to get started.")
                return True

            # Calculate statistics
            total_trees = len(trees_info)
            total_nodes = sum(tree["node_count"] for tree in trees_info)
            trees_with_nodes = sum(1 for tree in trees_info if tree["node_count"] > 0)
            empty_trees = total_trees - trees_with_nodes

            # Display statistics
            logger.info(f"\n--- Tree Statistics ---")
            logger.info(f"Total Trees: {total_trees}")
            logger.info(f"Total Nodes: {total_nodes}")
            logger.info(f"Trees with Nodes: {trees_with_nodes}")
            logger.info(f"Empty Trees: {empty_trees}")

            if total_trees > 0:
                avg_nodes = total_nodes / total_trees
                logger.info(f"Average Nodes per Tree: {avg_nodes:.1f}")

            # Display detailed tree list
            await self.execute(detailed=True)

            return True

        except Exception as e:
            logger.error(f"Error generating tree statistics: {e}")
            return False

    def get_tree_count(self) -> int:
        """
        Get the total number of available trees.

        Returns:
            Number of available trees
        """
        try:
            trees_info = self.tree_selection_service.get_available_trees_info()
            return len(trees_info)
        except Exception as e:
            logger.error(f"Error getting tree count: {e}")
            return 0

    def get_trees_summary(self) -> str:
        """
        Get a brief summary of available trees.

        Returns:
            Summary string of available trees
        """
        try:
            trees_info = self.tree_selection_service.get_available_trees_info()

            if not trees_info:
                return "No trees available"

            total_trees = len(trees_info)
            total_nodes = sum(tree["node_count"] for tree in trees_info)

            current_tree = next(
                (tree for tree in trees_info if tree["is_current"]), None
            )

            summary = f"{total_trees} trees, {total_nodes} total nodes"
            if current_tree:
                summary += f", current: {current_tree['name']}"
            else:
                summary += ", no tree selected"

            return summary

        except Exception as e:
            logger.error(f"Error generating trees summary: {e}")
            return "Error retrieving tree information"
