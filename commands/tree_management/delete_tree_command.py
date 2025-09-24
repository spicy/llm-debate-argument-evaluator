"""
DeleteTreeCommand - Delete debate trees with safety checks and confirmation.
"""

from typing import Optional
from uuid import UUID

from features.tree.tree_selection_service import TreeSelectionService
from utils.logger import logger


class DeleteTreeCommand:
    """
    Command for deleting debate trees.

    This command provides safe deletion of trees with confirmation prompts
    and automatic handling of current tree state when the active tree is deleted.
    """

    def __init__(self, tree_selection_service: TreeSelectionService):
        """
        Initialize the command with tree selection service.

        Args:
            tree_selection_service: Service for tree selection and management
        """
        self.tree_selection_service = tree_selection_service

    async def execute_current_tree(self, force: bool = False) -> bool:
        """
        Delete the currently selected tree.

        Args:
            force: Skip confirmation prompt if True

        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.tree_selection_service.state_service.has_current_tree:
            logger.warning("No tree currently selected for deletion")
            return False

        current_tree = self.tree_selection_service.state_service.current_tree
        logger.info(f"Attempting to delete current tree: {current_tree.display_name}")

        # Safety confirmation unless forced
        if not force and not self._confirm_deletion(current_tree.name):
            logger.info("Tree deletion cancelled by user")
            return False

        try:
            # Get tree info before deletion for logging
            tree_name = current_tree.name
            node_count = len(self.tree_selection_service.state_service.get_all_nodes())

            # Delete the tree
            success = (
                await self.tree_selection_service.state_service.delete_current_tree()
            )

            if success:
                logger.info(
                    f"Successfully deleted tree '{tree_name}' with {node_count} nodes"
                )

                # Try to auto-select another tree if available
                await self._handle_post_deletion_tree_selection()

                return True
            else:
                logger.error(f"Failed to delete tree '{tree_name}'")
                return False

        except Exception as e:
            logger.error(f"Error deleting current tree: {e}")
            return False

    async def execute_by_name(self, name: str, force: bool = False) -> bool:
        """
        Delete a tree by its name.

        Args:
            name: Name of the tree to delete
            force: Skip confirmation prompt if True

        Returns:
            True if deletion was successful, False otherwise
        """
        if not name or not name.strip():
            logger.error("Tree name cannot be empty")
            return False

        logger.info(f"Attempting to delete tree by name: '{name}'")

        try:
            # Find the tree
            trees = self.tree_selection_service.state_service.get_available_trees()
            target_tree = None

            for tree in trees:
                if tree.name.lower() == name.strip().lower():
                    target_tree = tree
                    break

            if not target_tree:
                logger.error(f"Tree with name '{name}' not found")
                return False

            # Safety confirmation unless forced
            if not force and not self._confirm_deletion(target_tree.name):
                logger.info("Tree deletion cancelled by user")
                return False

            # Check if this is the current tree
            is_current_tree = (
                self.tree_selection_service.state_service.has_current_tree
                and self.tree_selection_service.state_service.current_tree_id
                == target_tree.id
            )

            # Delete the tree
            success = self.tree_selection_service.state_service.tree_metadata_repository.delete_tree(
                target_tree.id
            )

            if success:
                node_count = (
                    self.tree_selection_service.state_service.repository.get_node_count(
                        target_tree.id
                    )
                )
                logger.info(
                    f"Successfully deleted tree '{target_tree.name}' with {node_count} nodes"
                )

                # If we deleted the current tree, handle the state
                if is_current_tree:
                    await self.tree_selection_service.state_service._clear_current_tree_state()
                    await self._handle_post_deletion_tree_selection()

                return True
            else:
                logger.error(f"Failed to delete tree '{target_tree.name}'")
                return False

        except Exception as e:
            logger.error(f"Error deleting tree '{name}': {e}")
            return False

    async def execute_by_id(self, tree_id: UUID, force: bool = False) -> bool:
        """
        Delete a tree by its UUID.

        Args:
            tree_id: UUID of the tree to delete
            force: Skip confirmation prompt if True

        Returns:
            True if deletion was successful, False otherwise
        """
        logger.info(f"Attempting to delete tree by ID: {tree_id}")

        try:
            # Get tree metadata for confirmation
            tree_metadata = self.tree_selection_service.state_service.tree_metadata_repository.get_tree(
                tree_id
            )

            if not tree_metadata:
                logger.error(f"Tree with ID {tree_id} not found")
                return False

            # Safety confirmation unless forced
            if not force and not self._confirm_deletion(tree_metadata.name):
                logger.info("Tree deletion cancelled by user")
                return False

            # Check if this is the current tree
            is_current_tree = (
                self.tree_selection_service.state_service.has_current_tree
                and self.tree_selection_service.state_service.current_tree_id == tree_id
            )

            # Delete the tree
            success = self.tree_selection_service.state_service.tree_metadata_repository.delete_tree(
                tree_id
            )

            if success:
                node_count = (
                    self.tree_selection_service.state_service.repository.get_node_count(
                        tree_id
                    )
                )
                logger.info(
                    f"Successfully deleted tree '{tree_metadata.name}' with {node_count} nodes"
                )

                # If we deleted the current tree, handle the state
                if is_current_tree:
                    await self.tree_selection_service.state_service._clear_current_tree_state()
                    await self._handle_post_deletion_tree_selection()

                return True
            else:
                logger.error(f"Failed to delete tree '{tree_metadata.name}'")
                return False

        except Exception as e:
            logger.error(f"Error deleting tree {tree_id}: {e}")
            return False

    async def execute_interactive(self) -> bool:
        """
        Execute the command with interactive tree selection for deletion.

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Show available trees
            trees_prompt = self.tree_selection_service.get_tree_selection_prompt()

            if "No trees available" in trees_prompt:
                logger.info("No trees available to delete")
                return False

            print("\n" + trees_prompt)

            # Get user selection
            choice = input(
                "\nEnter tree number to delete (or 'cancel' to abort): "
            ).strip()

            if choice.lower() in ["cancel", "c", "quit", "q"]:
                logger.info("Tree deletion cancelled by user")
                return False

            # Try to parse as index
            try:
                index = int(choice)
                trees = self.tree_selection_service.state_service.get_available_trees()

                if index < 1 or index > len(trees):
                    logger.error(f"Invalid selection: {index}")
                    return False

                selected_tree = trees[index - 1]
                return await self.execute_by_id(selected_tree.id, force=False)

            except ValueError:
                logger.error("Invalid selection. Please enter a number.")
                return False

        except KeyboardInterrupt:
            logger.info("Tree deletion cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Error during interactive tree deletion: {e}")
            return False

    def _confirm_deletion(self, tree_name: str) -> bool:
        """
        Prompt user for deletion confirmation with multiple confirmation methods.

        Args:
            tree_name: Name of the tree to be deleted

        Returns:
            True if user confirms deletion, False otherwise
        """
        try:
            # Step 1: Initial warning and simple confirmation
            warning_msg = (
                f"\n⚠️  WARNING: You are about to permanently delete tree '{tree_name}'\n"
                f"This will delete ALL nodes and data in this tree.\n"
                f"This action CANNOT be undone!\n"
            )
            print(warning_msg)

            # Simple yes/no first
            first_confirm = (
                input("Are you sure you want to delete this tree? (yes/no): ")
                .strip()
                .lower()
            )

            if self._is_cancellation(first_confirm):
                logger.info("Deletion cancelled by user at first confirmation")
                return False
            elif not self._is_simple_affirmative(first_confirm):
                print("❌ Deletion cancelled. Please type 'yes' or 'no'.")
                return False

            # Step 2: Double confirmation with tree name or safety phrase
            print("\n🔒 Final confirmation required for safety.")
            print(f"To proceed with deleting '{tree_name}', choose ONE of:")
            print(f"  1. Type the tree name exactly: '{tree_name}'")
            print("  2. Type 'DELETE' (uppercase)")
            print("  3. Type 'delete' (lowercase)")
            print("  4. Type 'confirm delete'")

            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                if attempt > 1:
                    print(f"\nAttempt {attempt} of {max_attempts}")

                final_confirm = input("\nFinal confirmation: ").strip()

                if self._is_valid_final_confirmation(final_confirm, tree_name):
                    logger.info(f"Deletion confirmed with: '{final_confirm}'")
                    print("✅ Deletion confirmed. Processing...")
                    return True
                elif self._is_cancellation(final_confirm):
                    logger.info("Deletion explicitly cancelled by user")
                    return False
                else:
                    print(f"❌ Invalid confirmation: '{final_confirm}'")
                    if attempt < max_attempts:
                        print(
                            "Please try again. You can type the tree name, 'DELETE', 'delete', or 'confirm delete'"
                        )
                    else:
                        print(
                            "❌ Maximum attempts reached. Deletion cancelled for safety."
                        )
                        logger.info(
                            f"Deletion cancelled after {max_attempts} invalid attempts"
                        )
                        return False

            return False

        except (KeyboardInterrupt, EOFError):
            logger.info("Deletion cancelled by user (Ctrl+C or EOF)")
            print("\n🛑 Deletion cancelled by user")
            return False

    def _is_simple_affirmative(self, response: str) -> bool:
        """Check if response is a simple yes."""
        return response.lower() in {"yes", "y", "yeah", "yep", "sure", "ok", "okay"}

    def _is_valid_final_confirmation(self, confirmation: str, tree_name: str) -> bool:
        """
        Check if the final confirmation input is valid for deletion.

        Args:
            confirmation: User input string
            tree_name: Expected tree name

        Returns:
            True if input confirms deletion, False otherwise
        """
        # Exact tree name match
        if confirmation == tree_name:
            return True

        # Standard deletion confirmations
        valid_confirmations = {
            "DELETE",
            "delete",
            "confirm delete",
            "CONFIRM DELETE",
            "Confirm Delete",
        }

        return confirmation in valid_confirmations

    def _is_cancellation(self, confirmation: str) -> bool:
        """
        Check if the confirmation input indicates cancellation.

        Args:
            confirmation: User input string

        Returns:
            True if input indicates cancellation, False otherwise
        """
        lower_conf = confirmation.lower()

        cancellation_phrases = {
            "no",
            "n",
            "cancel",
            "abort",
            "quit",
            "exit",
            "stop",
            "nope",
        }

        return lower_conf in cancellation_phrases

    async def _handle_post_deletion_tree_selection(self):
        """
        Handle tree selection after the current tree has been deleted.

        Attempts to auto-select another tree if available, or prompts to create a new one.
        """
        try:
            # Try to auto-select another tree
            success = await self.tree_selection_service.ensure_tree_selected()

            if success:
                current_tree = self.tree_selection_service.state_service.current_tree
                logger.info(f"Auto-selected tree: {current_tree.display_name}")
                return

            # No trees available - the main loop will handle tree creation prompting
            logger.info(
                "No other trees available after deletion - user will be prompted to create a new tree"
            )

        except Exception as e:
            logger.error(f"Error handling post-deletion tree selection: {e}")

    async def execute_cleanup_empty_trees(self, force: bool = False) -> int:
        """
        Delete all trees that have no nodes.

        Args:
            force: Skip confirmation prompt if True

        Returns:
            Number of trees deleted
        """
        try:
            trees_info = self.tree_selection_service.get_available_trees_info()
            empty_trees = [tree for tree in trees_info if tree["node_count"] == 0]

            if not empty_trees:
                logger.info("No empty trees found to clean up")
                return 0

            logger.info(f"Found {len(empty_trees)} empty trees")

            # Show empty trees
            for tree in empty_trees:
                logger.info(
                    f"  - {tree['name']} (created: {tree['created_at'].strftime('%Y-%m-%d') if tree['created_at'] else 'Unknown'})"
                )

            # Confirmation unless forced
            if not force:
                confirmation = (
                    input(f"\nDelete all {len(empty_trees)} empty trees? (y/N): ")
                    .strip()
                    .lower()
                )
                if confirmation not in ["y", "yes"]:
                    logger.info("Cleanup cancelled by user")
                    return 0

            # Delete empty trees
            deleted_count = 0
            for tree_info in empty_trees:
                try:
                    success = await self.execute_by_id(tree_info["id"], force=True)
                    if success:
                        deleted_count += 1
                except Exception as e:
                    logger.error(
                        f"Error deleting empty tree '{tree_info['name']}': {e}"
                    )

            logger.info(f"Successfully deleted {deleted_count} empty trees")
            return deleted_count

        except Exception as e:
            logger.error(f"Error during empty tree cleanup: {e}")
            return 0
