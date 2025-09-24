"""
CreateTreeCommand - Create a new tree with metadata and optionally switch to it.
"""

from features.tree.tree_selection_service import TreeSelectionService
from utils.logger import logger


class CreateTreeCommand:
    """
    Command for creating new debate trees.

    This command creates a new tree with the specified metadata and
    optionally switches to it immediately after creation.
    """

    def __init__(self, tree_selection_service: TreeSelectionService):
        """
        Initialize the command with tree selection service.

        Args:
            tree_selection_service: Service for tree selection and management
        """
        self.tree_selection_service = tree_selection_service

    async def execute(
        self,
        name: str,
        topic: str,
        description: str = None,
        switch_to_tree: bool = True,
    ) -> bool:
        """
        Create a new tree and optionally switch to it.

        Args:
            name: Name for the new tree (must be unique)
            topic: Topic for the new tree
            description: Optional description for the tree
            switch_to_tree: Whether to switch to the new tree after creation

        Returns:
            True if creation (and optional switch) was successful, False otherwise
        """
        logger.info(f"Creating new tree: '{name}' with topic: '{topic}'")

        # Validate input
        if not name or not name.strip():
            logger.error("Tree name cannot be empty")
            return False

        if not topic or not topic.strip():
            logger.error("Tree topic cannot be empty")
            return False

        # Validate name uniqueness and format
        is_valid, error_msg = self.tree_selection_service.validate_tree_name(name)
        if not is_valid:
            logger.error(f"Invalid tree name: {error_msg}")
            return False

        try:
            if switch_to_tree:
                # Use the service method that creates and switches
                success = (
                    await self.tree_selection_service.create_and_switch_to_new_tree(
                        name, topic, description
                    )
                )

                if success:
                    logger.info(f"Successfully created and switched to tree: '{name}'")
                    return True
                else:
                    logger.error(f"Failed to create tree: '{name}'")
                    return False
            else:
                # Create tree without switching
                new_tree = (
                    await self.tree_selection_service.state_service.create_new_tree(
                        name.strip(),
                        topic.strip(),
                        description.strip() if description else None,
                    )
                )

                if new_tree:
                    logger.info(f"Successfully created tree: '{new_tree.display_name}'")
                    return True
                else:
                    logger.error(f"Failed to create tree: '{name}'")
                    return False

        except Exception as e:
            logger.error(f"Error creating tree '{name}': {e}")
            return False

    async def execute_interactive(self) -> bool:
        """
        Execute the command with interactive prompts for input.

        Returns:
            True if creation was successful, False otherwise
        """
        try:
            # Get input from user
            name = input("Enter tree name: ").strip()
            if not name:
                logger.error("Tree name cannot be empty")
                return False

            topic = input("Enter tree topic: ").strip()
            if not topic:
                logger.error("Tree topic cannot be empty")
                return False

            description = input("Enter tree description (optional): ").strip()
            description = description if description else None

            # Ask if user wants to switch to the new tree
            switch_input = (
                input("Switch to the new tree after creation? (Y/n): ").strip().lower()
            )
            switch_to_tree = switch_input not in ["n", "no"]

            return await self.execute(name, topic, description, switch_to_tree)

        except KeyboardInterrupt:
            logger.info("Tree creation cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Error during interactive tree creation: {e}")
            return False
