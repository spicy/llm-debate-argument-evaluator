"""
TreeRepository - Handles CRUD operations for tree nodes with tree-scoped filtering.
"""

import threading
from typing import Any, Dict, List, Optional
from uuid import UUID

from infrastructure.database.supabase_service import SupabaseService
from utils.logger import logger


class TreeRepository:
    def __init__(self, supabase_service: SupabaseService):
        """Initialize the repository with a Supabase service."""
        self.client = supabase_service.get_client()
        self.table_name = "tree_nodes"
        self._lock = threading.Lock()
        logger.info("TreeRepository initialized.")

    def add_node(
        self, node_data: Dict[str, Any], tree_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Add a node to a specific tree.

        Args:
            node_data: Dictionary containing node information
            tree_id: UUID of the tree to add the node to

        Returns:
            Created node data with database-generated ID, or None if creation failed
        """
        with self._lock:
            try:
                # Ensure tree_id is included in the node data
                node_data_with_tree = node_data.copy()
                node_data_with_tree["tree_id"] = str(tree_id)

                response = (
                    self.client.table(self.table_name)
                    .insert(node_data_with_tree)
                    .execute()
                )
                if response.data:
                    logger.debug(
                        f"Added node to tree {tree_id}: {response.data[0]['id']}"
                    )
                    return response.data[0]
                return None
            except Exception as e:
                logger.error(f"Error adding node to tree {tree_id}: {e}")
                return None

    def get_node(self, node_id: int, tree_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get a specific node from a specific tree.

        Args:
            node_id: ID of the node to retrieve
            tree_id: UUID of the tree containing the node

        Returns:
            Node data dictionary if found, None otherwise
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("id", node_id)
                .eq("tree_id", str(tree_id))
                .execute()
            )
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting node {node_id} from tree {tree_id}: {e}")
            return None

    def get_children(self, parent_id: int, tree_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all children of a specific node within a specific tree.

        Args:
            parent_id: ID of the parent node
            tree_id: UUID of the tree containing the nodes

        Returns:
            List of child node data dictionaries
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("parent_id", parent_id)
                .eq("tree_id", str(tree_id))
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(
                f"Error getting children for parent {parent_id} in tree {tree_id}: {e}"
            )
            return []

    def get_all_nodes(self, tree_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all nodes from a specific tree.

        Args:
            tree_id: UUID of the tree to get nodes from

        Returns:
            List of all node data dictionaries in the tree
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("tree_id", str(tree_id))
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting all nodes from tree {tree_id}: {e}")
            return []

    def update_node(
        self, node_id: int, update_data: Dict[str, Any], tree_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Update a specific node within a specific tree.

        Args:
            node_id: ID of the node to update
            update_data: Dictionary of fields to update
            tree_id: UUID of the tree containing the node

        Returns:
            Updated node data dictionary if successful, None otherwise
        """
        with self._lock:
            try:
                # Ensure we don't allow updating tree_id through this method
                safe_update_data = update_data.copy()
                safe_update_data.pop("tree_id", None)

                response = (
                    self.client.table(self.table_name)
                    .update(safe_update_data)
                    .eq("id", node_id)
                    .eq("tree_id", str(tree_id))
                    .execute()
                )
                if response.data:
                    logger.debug(f"Updated node {node_id} in tree {tree_id}.")
                    return response.data[0]
                return None
            except Exception as e:
                logger.error(f"Error updating node {node_id} in tree {tree_id}: {e}")
                return None

    def node_exists(self, node_id: int, tree_id: UUID) -> bool:
        """
        Check if a specific node exists within a specific tree.

        Args:
            node_id: ID of the node to check
            tree_id: UUID of the tree to check in

        Returns:
            True if node exists in the tree, False otherwise
        """
        return self.get_node(node_id, tree_id) is not None

    def delete_node(self, node_id: int, tree_id: UUID) -> bool:
        """
        Delete a specific node from a tree.

        Args:
            node_id: ID of the node to delete
            tree_id: UUID of the tree containing the node

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            with self._lock:
                response = (
                    self.client.table(self.table_name)
                    .delete()
                    .eq("id", node_id)
                    .eq("tree_id", str(tree_id))
                    .execute()
                )

                if response.data:
                    logger.debug(f"Deleted node {node_id} from tree {tree_id}")
                    return True
                else:
                    logger.warning(
                        f"Node {node_id} not found for deletion in tree {tree_id}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error deleting node {node_id} from tree {tree_id}: {e}")
            return False

    async def delete_all_nodes_in_tree(self, tree_id: UUID):
        """
        Delete all nodes from a specific tree.

        Args:
            tree_id: UUID of the tree to clear

        Returns:
            Database response if successful, None otherwise
        """
        try:
            with self._lock:
                response = (
                    self.client.table(self.table_name)
                    .delete()
                    .eq("tree_id", str(tree_id))
                    .execute()
                )
            logger.info(f"All nodes have been deleted from tree {tree_id}.")
            return response
        except Exception as e:
            logger.error(f"Error deleting all nodes from tree {tree_id}: {e}")
            return None

    def get_root_node(self, tree_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get the root node of a specific tree.

        Args:
            tree_id: UUID of the tree to get root node from

        Returns:
            Root node data dictionary if found, None otherwise
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("tree_id", str(tree_id))
                .is_("parent_id", "null")
                .execute()
            )
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting root node from tree {tree_id}: {e}")
            return None

    def get_node_count(self, tree_id: UUID) -> int:
        """
        Get the total number of nodes in a specific tree.

        Args:
            tree_id: UUID of the tree to count nodes in

        Returns:
            Number of nodes in the tree
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("id", count="exact")
                .eq("tree_id", str(tree_id))
                .execute()
            )
            return response.count or 0
        except Exception as e:
            logger.error(f"Error counting nodes in tree {tree_id}: {e}")
            return 0
