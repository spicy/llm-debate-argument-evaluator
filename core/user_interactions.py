"""
TODO: This module...
"""

import asyncio
from typing import TYPE_CHECKING

from utils.logger import logger
from visualization.renderer_factory import get_renderer_info
from config.visualization_config import visualization_config
from core.user_command_registry import UserCommandRegistry

if TYPE_CHECKING:
    from core.controller import Controller


class UserInteractions:
    def __init__(self):
        """User interactions manager using a command registry"""
        self.controller: "Controller" = None
        self.command_registry: UserCommandRegistry = None
        self.commands = []  # Will be populated when controller is set

    def initialize_commands(self, controller):
        """Initialize the command registry with the controller"""
        self.controller = controller
        self.command_registry = UserCommandRegistry(controller)
        self.commands = self.command_registry.get_command_list()

    async def get_numbered_selection(
        self, prompt: str, options: list, get_display_text=None, is_async=True
    ) -> str:
        """
        Generic function for numbered selection from a list of options.

        Args:
            prompt: The prompt to display to the user
            options: List of options to choose from
            get_display_text: Optional function to format display text for each option
            is_async: Whether to use async input (default True)

        Returns:
            The selected option
        """
        display_prompt = prompt + "\n"

        for i, option in enumerate(options, 1):
            if get_display_text:
                display_text = get_display_text(option, i)
            else:
                display_text = f"{i}. {option}"
            display_prompt += f"  {display_text}\n"

        display_prompt += f"Enter your choice (1-{len(options)}): "

        while True:
            try:
                if is_async:
                    choice_input = await asyncio.to_thread(input, display_prompt)
                else:
                    choice_input = input(display_prompt)

                # Strip whitespace and ensure we have the full input
                choice_input = choice_input.strip()

                if not choice_input:
                    logger.warning("Please enter a number.")
                    continue

                choice = int(choice_input)
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                else:
                    logger.warning(
                        f"Invalid choice: {choice}. Please select a number between 1 and {len(options)}."
                    )
                    continue
            except ValueError:
                logger.warning(
                    f"Invalid input '{choice_input}'. Please enter a valid number."
                )
                continue

    def get_numbered_selection_sync(
        self, prompt: str, options: list, get_display_text=None
    ) -> str:
        """
        Synchronous version of numbered selection for non-async contexts.
        """
        display_prompt = prompt + "\n"

        for i, option in enumerate(options, 1):
            if get_display_text:
                display_text = get_display_text(option, i)
            else:
                display_text = f"{i}. {option}"
            display_prompt += f"  {display_text}\n"

        display_prompt += f"Enter your choice (1-{len(options)}): "

        while True:
            try:
                choice_input = input(display_prompt)

                # Strip whitespace and ensure we have the full input
                choice_input = choice_input.strip()

                if not choice_input:
                    logger.warning("Please enter a number.")
                    continue

                choice = int(choice_input)
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                else:
                    logger.warning(
                        f"Invalid choice: {choice}. Please select a number between 1 and {len(options)}."
                    )
                    continue
            except ValueError:
                logger.warning(
                    f"Invalid input '{choice_input}'. Please enter a valid number."
                )
                continue

    def get_renderer_type(self) -> str:
        """Prompts the user to select a renderer and returns their choice."""
        # Check if renderer type is already configured
        if visualization_config.RENDERER_TYPE is not None:
            logger.info(
                f"Using configured renderer: {visualization_config.RENDERER_TYPE}"
            )
            return visualization_config.RENDERER_TYPE

        renderer_info = get_renderer_info()
        renderers = list(renderer_info.keys())

        def format_renderer_option(renderer, index):
            return f"{index}. {renderer.capitalize()} - {renderer_info[renderer]['description']}"

        return self.get_numbered_selection_sync(
            "Select a renderer for visualization:", renderers, format_renderer_option
        )

    async def main_loop(self):
        """Main interaction loop using dynamic command discovery"""
        # Ensure a tree is selected on startup
        await self._ensure_tree_available_on_startup()

        while True:
            # Check if we still have a tree selected (might have been deleted)
            await self._ensure_tree_available()

            # Show current tree context
            await self._display_tree_context()

            # Extract just command names for the selection utility
            command_options = [cmd for cmd, desc in self.commands]

            def format_command_option(command, index):
                # Find the description for this command
                desc = next(desc for cmd, desc in self.commands if cmd == command)
                return f"{index:2}. {command:<15} {desc}"

            command = await self.get_numbered_selection(
                "Select a command:",
                command_options,
                format_command_option,
                is_async=True,
            )

            # Execute command using the registry
            try:
                should_quit = await self.command_registry.execute_command(command)
                if should_quit:
                    break
            except Exception as e:
                logger.error(f"Error executing command '{command}': {e}", exc_info=True)

    async def _ensure_tree_available_on_startup(self):
        """Ensure a tree is available when the application starts."""
        try:
            # Check if any trees exist
            list_trees_command = self.controller.injector.get("list_trees_command")
            tree_count = list_trees_command.get_tree_count()

            if tree_count == 0:
                # No trees exist, prompt user to create one
                logger.info(
                    "Welcome! No trees found. Let's create your first debate tree."
                )
                print("\n" + "=" * 60)
                print("🌳 WELCOME TO LLM DEBATE ARGUMENT EVALUATOR 🌳")
                print("=" * 60)
                print("No debate trees found. Let's create your first tree!")
                print("=" * 60)

                await self._prompt_tree_creation()
            else:
                # Trees exist, ensure one is selected
                await self.controller.ensure_tree_selected()

        except Exception as e:
            logger.error(f"Error during startup tree setup: {e}")

    async def _ensure_tree_available(self):
        """Ensure a tree is available during normal operation."""
        try:
            # Check if any trees exist
            list_trees_command = self.controller.injector.get("list_trees_command")
            tree_count = list_trees_command.get_tree_count()

            if tree_count == 0:
                # No trees exist after deletion, prompt user to create one
                logger.info("No trees available. Prompting to create a new tree.")
                print("\n" + "=" * 60)
                print("🌳 NO TREES REMAINING")
                print("=" * 60)
                print("All trees have been deleted. Let's create a new tree!")
                print("=" * 60)

                await self._prompt_tree_creation()
            else:
                # Trees exist, ensure one is selected
                switch_tree_command = self.controller.injector.get(
                    "switch_tree_command"
                )
                if (
                    not switch_tree_command.tree_selection_service.state_service.has_current_tree
                ):
                    await self.controller.ensure_tree_selected()

        except Exception as e:
            logger.error(f"Error ensuring tree availability: {e}")

    async def _prompt_tree_creation(self):
        """Prompt user to create a new tree."""
        try:
            create_tree_command = self.controller.injector.get("create_tree_command")
            success = await create_tree_command.execute_interactive()

            if not success:
                logger.warning("Failed to create tree. Some features may not work.")
                print(
                    "\n⚠️ No tree was created. You can create one later using the 'create-tree' command."
                )
        except Exception as e:
            logger.error(f"Error during tree creation prompt: {e}")

    async def _display_tree_context(self):
        """Display current tree context before showing the command menu."""
        try:
            # Get current tree info
            switch_tree_command = self.controller.injector.get("switch_tree_command")
            current_summary = (
                switch_tree_command.tree_selection_service.get_current_tree_summary()
            )

            # Get overall tree stats
            list_trees_command = self.controller.injector.get("list_trees_command")
            trees_summary = list_trees_command.get_trees_summary()

            print("\n" + "=" * 60)
            print("🌳 LLM DEBATE ARGUMENT EVALUATOR")
            print("=" * 60)

            if current_summary:
                print("📍 Current Tree:")
                # Format the summary nicely
                lines = current_summary.split("\n")
                for line in lines:
                    print(f"   {line}")
            else:
                print("📍 No tree currently selected")

            print(f"📊 System: {trees_summary}")
            print("=" * 60)

        except Exception as e:
            logger.error(f"Error displaying tree context: {e}")
            print("\n" + "=" * 60)
            print("🌳 LLM DEBATE ARGUMENT EVALUATOR")
            print("=" * 60)
