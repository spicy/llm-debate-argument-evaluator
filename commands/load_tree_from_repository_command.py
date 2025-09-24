"""
This module defines the command for loading an existing tree from the repository.
"""

from typing import Optional
from uuid import UUID

from features.tree.multi_tree_state_service import MultiTreeStateService
from utils.logger import logger


class LoadTreeFromRepositoryCommand:
    def __init__(self, tree_state_service: MultiTreeStateService):
        """
        Initialize the command with a multi-tree state service.

        Args:
            tree_state_service: Multi-tree state service
        """
        self.tree_state_service = tree_state_service

    async def execute(self, tree_id: Optional[UUID] = None):
        """
        Load a specific tree or the first available tree from the repository.

        Args:
            tree_id: UUID of specific tree to load. If None, loads first available tree.
        """
        if tree_id:
            logger.info(f"Loading specific tree: {tree_id}")
        else:
            logger.info("Loading first available tree from repository")

        await self.tree_state_service.load_tree_from_repository(tree_id)
