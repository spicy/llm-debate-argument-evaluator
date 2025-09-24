"""
RenameTreeCommand - Rename existing debate trees with validation.
"""

from typing import Optional
from uuid import UUID

from features.tree.tree_selection_service import TreeSelectionService
from utils.logger import logger


class RenameTreeCommand:
    """
    Command for renaming debate trees.

    This command allows users to rename existing trees with proper validation
    to ensure name uniqueness and format requirements.
    """

    def __init__(self, tree_selection_service: TreeSelectionService):
        """
        Initialize the command with tree selection service.

        Args:
            tree_selection_service: Service for tree selection and management
        """
        self.tree_selection_service = tree_selection_service

    async def execute_current_tree(self, new_name: str) -> bool:
        """
        Rename the currently selected tree.

        Args:
            new_name: New name for the tree

        Returns:
            True if rename was successful, False otherwise
        """
        if not self.tree_selection_service.state_service.has_current_tree:
            logger.error("No tree currently selected for renaming")
            return False

        current_tree = self.tree_selection_service.state_service.current_tree
        old_name = current_tree.name

        logger.info(f"Renaming current tree from '{old_name}' to '{new_name}'")

        return await self._perform_rename(current_tree.id, old_name, new_name)

    async def execute_by_name(self, old_name: str, new_name: str) -> bool:
        """
        Rename a tree by its current name.

        Args:
            old_name: Current name of the tree
            new_name: New name for the tree

        Returns:
            True if rename was successful, False otherwise
        """
        if not old_name or not old_name.strip():
            logger.error("Current tree name cannot be empty")
            return False

        logger.info(f"Renaming tree from '{old_name}' to '{new_name}'")

        try:
            # Find the tree
            trees = self.tree_selection_service.state_service.get_available_trees()
            target_tree = None

            for tree in trees:
                if tree.name.lower() == old_name.strip().lower():
                    target_tree = tree
                    break

            if not target_tree:
                logger.error(f"Tree with name '{old_name}' not found")
                return False

            return await self._perform_rename(target_tree.id, old_name, new_name)

        except Exception as e:
            logger.error(f"Error renaming tree '{old_name}': {e}")
            return False

    async def execute_by_id(self, tree_id: UUID, new_name: str) -> bool:
        """
        Rename a tree by its UUID.

        Args:
            tree_id: UUID of the tree to rename
            new_name: New name for the tree

        Returns:
            True if rename was successful, False otherwise
        """
        logger.info(f"Renaming tree {tree_id} to '{new_name}'")

        try:
            # Get current tree metadata
            tree_metadata = self.tree_selection_service.state_service.tree_metadata_repository.get_tree(
                tree_id
            )

            if not tree_metadata:
                logger.error(f"Tree with ID {tree_id} not found")
                return False

            old_name = tree_metadata.name
            return await self._perform_rename(tree_id, old_name, new_name)

        except Exception as e:
            logger.error(f"Error renaming tree {tree_id}: {e}")
            return False

    async def _perform_rename(
        self, tree_id: UUID, old_name: str, new_name: str
    ) -> bool:
        """
        Perform the actual rename operation with validation.

        Args:
            tree_id: UUID of the tree to rename
            old_name: Current name of the tree
            new_name: New name for the tree

        Returns:
            True if rename was successful, False otherwise
        """
        try:
            # Validate new name
            if not new_name or not new_name.strip():
                logger.error("New tree name cannot be empty")
                return False

            new_name = new_name.strip()

            # Check if the name is actually changing
            if new_name.lower() == old_name.lower():
                logger.info("New name is the same as current name - no change needed")
                return True

            # Validate name format and uniqueness (excluding current tree)
            is_valid, error_msg = self._validate_new_name(new_name, tree_id)
            if not is_valid:
                logger.error(f"Invalid new name: {error_msg}")
                return False

            # Perform the rename
            updated_tree = self.tree_selection_service.state_service.tree_metadata_repository.update_tree(
                tree_id, {"name": new_name}
            )

            if updated_tree:
                logger.info(
                    f"Successfully renamed tree from '{old_name}' to '{new_name}'"
                )

                # Update current tree object if this is the current tree
                if (
                    self.tree_selection_service.state_service.has_current_tree
                    and self.tree_selection_service.state_service.current_tree_id
                    == tree_id
                ):
                    self.tree_selection_service.state_service.current_tree = (
                        updated_tree
                    )

                return True
            else:
                logger.error(f"Failed to rename tree '{old_name}'")
                return False

        except Exception as e:
            logger.error(
                f"Error performing rename from '{old_name}' to '{new_name}': {e}"
            )
            return False

    def _validate_new_name(self, name: str, exclude_tree_id: UUID) -> tuple[bool, str]:
        """
        Validate the new tree name.

        Args:
            name: Name to validate
            exclude_tree_id: Tree ID to exclude from uniqueness check

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic format validation
        if len(name) < 3:
            return False, "Tree name must be at least 3 characters long"

        if len(name) > 100:
            return False, "Tree name must be less than 100 characters"

        # Check uniqueness (excluding the tree being renamed)
        if self.tree_selection_service.state_service.tree_metadata_repository.name_exists(
            name, exclude_tree_id
        ):
            return False, f"Tree with name '{name}' already exists"

        return True, ""

    async def execute_interactive(self) -> bool:
        """
        Execute the command with interactive prompts.

        Returns:
            True if rename was successful, False otherwise
        """
        try:
            # Check if current tree exists
            if self.tree_selection_service.state_service.has_current_tree:
                current_tree = self.tree_selection_service.state_service.current_tree
                current_prompt = f"Current tree: '{current_tree.name}'\n"
                use_current = (
                    input(f"{current_prompt}Rename current tree? (Y/n): ")
                    .strip()
                    .lower()
                )

                if use_current in ["", "y", "yes"]:
                    new_name = input(
                        f"Enter new name for '{current_tree.name}': "
                    ).strip()
                    if new_name:
                        return await self.execute_current_tree(new_name)
                    else:
                        logger.error("New name cannot be empty")
                        return False

            # Show available trees for selection
            trees_prompt = self.tree_selection_service.get_tree_selection_prompt()

            if "No trees available" in trees_prompt:
                logger.info("No trees available to rename")
                return False

            print("\n" + trees_prompt)

            # Get user selection
            choice = input(
                "\nEnter tree number to rename (or 'cancel' to abort): "
            ).strip()

            if choice.lower() in ["cancel", "c", "quit", "q"]:
                logger.info("Tree rename cancelled by user")
                return False

            # Try to parse as index
            try:
                index = int(choice)
                trees = self.tree_selection_service.state_service.get_available_trees()

                if index < 1 or index > len(trees):
                    logger.error(f"Invalid selection: {index}")
                    return False

                selected_tree = trees[index - 1]
                new_name = input(f"Enter new name for '{selected_tree.name}': ").strip()

                if new_name:
                    return await self.execute_by_id(selected_tree.id, new_name)
                else:
                    logger.error("New name cannot be empty")
                    return False

            except ValueError:
                logger.error("Invalid selection. Please enter a number.")
                return False

        except KeyboardInterrupt:
            logger.info("Tree rename cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Error during interactive tree rename: {e}")
            return False
