"""
MultiTreeStateService - Enhanced state management for multiple trees.
"""

from heapq import heappop, heappush
from typing import Any, Dict, List, Optional
from uuid import UUID
import threading
import asyncio

from features.tree.models.tree import Tree
from features.tree.tree_data_service import TreeDataService
from features.tree.tree_repository import TreeRepository
from features.tree.tree_metadata_repository import TreeMetadataRepository
from utils.subject import Subject
from utils.logger import logger


class MultiTreeStateService(Subject, TreeDataService):
    """
    Enhanced tree state service that manages multiple trees with switching capability.

    This service maintains the in-memory state of the currently selected tree while
    providing functionality to switch between different trees. Only one tree is
    loaded in memory at a time for performance efficiency.
    """

    def __init__(
        self,
        repository: TreeRepository,
        tree_metadata_repository: TreeMetadataRepository,
    ):
        """
        Initialize the service with repositories.

        Args:
            repository: TreeRepository for node operations
            tree_metadata_repository: TreeMetadataRepository for tree metadata operations
        """
        super().__init__()
        self.repository = repository
        self.tree_metadata_repository = tree_metadata_repository

        # Current tree state
        self.current_tree: Optional[Tree] = None
        self.tree: Dict[str, Any] = {}  # In-memory nodes of current tree
        self.optimal_path: List[Dict[str, Any]] = []

        # Thread safety
        self._lock = threading.Lock()

        logger.info("MultiTreeStateService initialized")

    @property
    def current_tree_id(self) -> Optional[UUID]:
        """Get the ID of the currently loaded tree."""
        return self.current_tree.id if self.current_tree else None

    @property
    def has_current_tree(self) -> bool:
        """Check if a tree is currently loaded."""
        return self.current_tree is not None

    @property
    def current_tree_info(self) -> Optional[str]:
        """Get display information about the current tree."""
        if self.current_tree:
            return f"{self.current_tree.display_name} (Nodes: {len(self.tree)})"
        return None

    async def switch_to_tree(self, tree_id: UUID) -> bool:
        """
        Switch to a different tree, loading its nodes into memory.

        Args:
            tree_id: UUID of the tree to switch to

        Returns:
            True if switch was successful, False otherwise
        """
        with self._lock:
            try:
                # Get tree metadata
                target_tree = self.tree_metadata_repository.get_tree(tree_id)
                if not target_tree:
                    logger.error(f"Tree with ID {tree_id} not found")
                    return False

                # If already on this tree, do nothing
                if self.current_tree and self.current_tree.id == tree_id:
                    logger.info(f"Already switched to tree: {target_tree.display_name}")
                    return True

                # Clear current tree state
                await self._clear_current_tree_state()

                # Load new tree
                await self._load_tree_into_memory(target_tree)

                logger.info(
                    f"Successfully switched to tree: {target_tree.display_name}"
                )
                return True

            except Exception as e:
                logger.error(f"Error switching to tree {tree_id}: {e}")
                return False

    async def _clear_current_tree_state(self):
        """Clear the current tree from memory."""
        if self.current_tree:
            logger.debug(f"Clearing tree from memory: {self.current_tree.display_name}")

        self.current_tree = None
        self.tree.clear()
        self.optimal_path = []

    async def _load_tree_into_memory(self, tree: Tree):
        """
        Load a tree's nodes into memory.

        Args:
            tree: Tree metadata object
        """
        self.current_tree = tree

        # Load all nodes for this tree
        all_nodes = self.repository.get_all_nodes(tree.id)

        if not all_nodes:
            logger.info(f"No nodes found for tree: {tree.display_name}")
        else:
            for node in all_nodes:
                await self._load_node_into_memory(node)

            logger.info(f"Loaded {len(all_nodes)} nodes for tree: {tree.display_name}")

        # Notify observers of the tree change
        await self.notify(self.tree, self.optimal_path)

    async def _load_node_into_memory(self, node: Dict[str, Any]):
        """Load a single node into memory without notifications."""
        node_id = str(node.get("id"))
        if node_id in self.tree:
            return  # Avoid duplication

        self.tree[node_id] = node

    def _load_node_into_memory_sync(self, node: Dict[str, Any]):
        """Load a single node into memory synchronously without notifications."""
        node_id = str(node.get("id"))
        if node_id in self.tree:
            return  # Avoid duplication

        self.tree[node_id] = node

    def add_node(self, node_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a node to the current tree.

        Args:
            node_data: Dictionary containing node information

        Returns:
            Created node data with database-generated ID, or None if creation failed
        """
        if not self.has_current_tree:
            logger.error("No tree currently selected for adding nodes")
            return None

        # Persist first to get a database-generated ID
        new_node_from_db = self.repository.add_node(node_data, self.current_tree_id)
        if not new_node_from_db:
            logger.error("Failed to add node to the database.")
            return None

        # Add the complete node to the in-memory state synchronously to avoid race conditions
        self._load_node_into_memory_sync(new_node_from_db)

        # Schedule async notification
        asyncio.create_task(self.notify(self.tree, self.optimal_path))
        return new_node_from_db

    async def _add_node_to_memory(self, node: Dict[str, Any]):
        """Add a node to memory and notify observers."""
        await self._load_node_into_memory(node)
        await self.notify(self.tree, self.optimal_path)

    async def load_tree_from_repository(self, tree_id: Optional[UUID] = None):
        """
        Load a specific tree from the repository into memory.

        Args:
            tree_id: UUID of tree to load. If None, tries to load the first available tree.
        """
        if tree_id:
            success = await self.switch_to_tree(tree_id)
            if not success:
                logger.error(f"Failed to load tree {tree_id}")
        else:
            # Try to load the first available tree
            available_trees = self.tree_metadata_repository.list_trees(limit=1)
            if available_trees:
                await self.switch_to_tree(available_trees[0].id)
            else:
                logger.info("No trees available to load")

    async def update_node(self, node_id: str, updates: Dict[str, Any]):
        """
        Update a node in the current tree.

        Args:
            node_id: ID of the node to update
            updates: Dictionary of fields to update
        """
        if not self.has_current_tree:
            logger.error("No tree currently selected for updating nodes")
            return

        node_id_str = str(node_id)
        if node_id_str not in self.tree:
            logger.warning(f"Node with ID {node_id_str} not found for update.")
            return

        # Update in memory
        self.tree[node_id_str].update(updates)

        # Update in database - only pass the updates, not the full node
        self.repository.update_node(int(node_id_str), updates, self.current_tree_id)

        # Notify observers
        await self.notify(self.tree, self.optimal_path)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a node from the current tree.

        Args:
            node_id: ID of the node to retrieve

        Returns:
            Node data dictionary if found, None otherwise
        """
        return self.tree.get(str(node_id))

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """
        Get all nodes from the current tree.

        Returns:
            List of all node data dictionaries in the current tree
        """
        return list(self.tree.values())

    def get_children(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Get all children of a specific node in the current tree.

        Args:
            node_id: ID of the parent node

        Returns:
            List of child node data dictionaries
        """
        children = []
        node_id_str = str(node_id)
        for node in self.tree.values():
            if str(node.get("parent_id")) == node_id_str:
                children.append(node)
        return children

    async def set_optimal_path(self, path: List[Dict[str, Any]]):
        """
        Set the optimal path for the current tree.

        Args:
            path: List of nodes representing the optimal path
        """
        self.optimal_path = path
        await self.notify(self.tree, self.optimal_path)

    async def reset_current_tree(self):
        """Reset the current tree, clearing all its nodes."""
        if not self.has_current_tree:
            logger.warning("No tree currently selected for reset")
            return

        # Clear nodes from database
        await self.repository.delete_all_nodes_in_tree(self.current_tree_id)

        # Clear in-memory state
        self.tree.clear()
        self.optimal_path = []

        # Notify observers
        await self.notify(self.tree, self.optimal_path)

        logger.info(f"Reset tree: {self.current_tree.display_name}")

    async def delete_current_tree(self):
        """Delete the current tree entirely (metadata and all nodes)."""
        if not self.has_current_tree:
            logger.warning("No tree currently selected for deletion")
            return False

        tree_name = self.current_tree.display_name
        tree_id = self.current_tree_id

        try:
            # Delete tree metadata (cascade will delete nodes)
            success = self.tree_metadata_repository.delete_tree(tree_id)

            if success:
                # Clear current state
                await self._clear_current_tree_state()
                await self.notify(self.tree, self.optimal_path)

                logger.info(f"Deleted tree: {tree_name}")
                return True
            else:
                logger.error(f"Failed to delete tree: {tree_name}")
                return False

        except Exception as e:
            logger.error(f"Error deleting tree {tree_name}: {e}")
            return False

    def get_available_trees(self) -> List[Tree]:
        """
        Get a list of all available trees.

        Returns:
            List of Tree metadata objects
        """
        return self.tree_metadata_repository.list_trees()

    async def create_new_tree(
        self, name: str, topic: str, description: str = None
    ) -> Optional[Tree]:
        """
        Create a new tree and optionally switch to it.

        Args:
            name: Name for the new tree
            topic: Topic for the new tree
            description: Optional description

        Returns:
            Created Tree object if successful, None otherwise
        """
        try:
            # Check if name already exists
            if self.tree_metadata_repository.name_exists(name):
                logger.error(f"Tree name '{name}' already exists")
                return None

            # Create tree metadata
            new_tree = Tree(name=name, topic=topic, description=description)
            created_tree = self.tree_metadata_repository.create_tree(new_tree)

            if created_tree:
                logger.info(f"Created new tree: {created_tree.display_name}")
                return created_tree
            else:
                logger.error("Failed to create tree metadata")
                return None

        except Exception as e:
            logger.error(f"Error creating new tree '{name}': {e}")
            return None
