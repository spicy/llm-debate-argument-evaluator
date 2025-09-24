"""
User command registry - defines all user-facing commands in a single place.
This avoids file proliferation while keeping command metadata organized.
"""

from typing import Dict, List, Any, Callable, Awaitable
from dataclasses import dataclass
import asyncio

from utils.logger import logger


@dataclass
class UserCommandInput:
    """Defines an input field for a user command"""

    name: str
    prompt: str
    default: str = None
    required: bool = True
    input_type: str = "str"  # "str", "int", "float"


@dataclass
class UserCommand:
    """Defines a complete user command with metadata and handler"""

    name: str
    description: str
    inputs: List[UserCommandInput]
    handler: Callable[..., Awaitable[bool]]  # Returns True if should quit


class UserCommandRegistry:
    """Registry of all user commands with their metadata and handlers"""

    def __init__(self, controller):
        self.controller = controller
        self._commands = self._build_commands()

    def _build_commands(self) -> Dict[str, UserCommand]:
        """Build the command registry"""
        return {
            "start": UserCommand(
                name="start",
                description="Run the complete tree process using the current tree's topic.",
                inputs=[
                    UserCommandInput(
                        "depth",
                        "Enter maximum depth",
                        default="3",
                        required=False,
                        input_type="int",
                    ),
                ],
                handler=self._handle_start,
            ),
            "build": UserCommand(
                name="build",
                description="Build out the tree from a specific node.",
                inputs=[
                    UserCommandInput(
                        "node_id", "Enter root node ID to build from", required=True
                    ),
                    UserCommandInput(
                        "depth",
                        "Enter maximum depth (relative to selected node)",
                        default="3",
                        required=False,
                        input_type="int",
                    ),
                ],
                handler=self._handle_build,
            ),
            "expand": UserCommand(
                name="expand",
                description="Expand a node with new generated arguments.",
                inputs=[
                    UserCommandInput(
                        "node_id", "Enter node ID to expand", required=True
                    )
                ],
                handler=self._handle_expand,
            ),
            "submit": UserCommand(
                name="submit",
                description="Submit a new argument to the current tree.",
                inputs=[
                    UserCommandInput("argument", "Enter your argument", required=True),
                    UserCommandInput("category", "Enter category", required=True),
                ],
                handler=self._handle_submit,
            ),
            "generate": UserCommand(
                name="generate",
                description="Generate new arguments for a specific node.",
                inputs=[
                    UserCommandInput(
                        "node_id",
                        "Enter node ID to generate arguments for",
                        required=True,
                    ),
                    UserCommandInput(
                        "num_arguments",
                        "Enter number of arguments to generate",
                        default="4",
                        required=False,
                        input_type="int",
                    ),
                ],
                handler=self._handle_generate,
            ),
            "evaluate": UserCommand(
                name="evaluate",
                description="Evaluate a single node in the tree.",
                inputs=[
                    UserCommandInput(
                        "node_id",
                        "Enter node ID to evaluate",
                        required=True,
                        input_type="int",
                    )
                ],
                handler=self._handle_evaluate,
            ),
            "load": UserCommand(
                name="load",
                description="Load a tree from a JSON file.",
                inputs=[
                    UserCommandInput(
                        "file_path", "Enter the path to the JSON file", required=True
                    )
                ],
                handler=self._handle_load,
            ),
            "list": UserCommand(
                name="list",
                description="List all nodes in the current tree.",
                inputs=[],
                handler=self._handle_list,
            ),
            "path": UserCommand(
                name="path",
                description="Show the current optimal path in the tree.",
                inputs=[],
                handler=self._handle_path,
            ),
            "reset": UserCommand(
                name="reset",
                description="Reset the current tree, clearing all data.",
                inputs=[],
                handler=self._handle_reset,
            ),
            "prune": UserCommand(
                name="prune",
                description="Prune low-quality branches from the tree.",
                inputs=[
                    UserCommandInput(
                        "threshold",
                        "Enter pruning threshold (0.0-1.0) - removes nodes with paths below this score",
                        default="0.6",
                        required=True,
                        input_type="float",
                    )
                ],
                handler=self._handle_prune,
            ),
            # Tree Management Commands
            "create-tree": UserCommand(
                name="create-tree",
                description="Create a new debate tree.",
                inputs=[
                    UserCommandInput("name", "Enter tree name", required=True),
                    UserCommandInput("topic", "Enter tree topic", required=True),
                    UserCommandInput(
                        "description", "Enter description (optional)", required=False
                    ),
                ],
                handler=self._handle_create_tree,
            ),
            "switch-tree": UserCommand(
                name="switch-tree",
                description="Switch to a different tree.",
                inputs=[],
                handler=self._handle_switch_tree,
            ),
            "list-trees": UserCommand(
                name="list-trees",
                description="List all available trees.",
                inputs=[],
                handler=self._handle_list_trees,
            ),
            "delete-tree": UserCommand(
                name="delete-tree",
                description="Delete a tree (with confirmation).",
                inputs=[],
                handler=self._handle_delete_tree,
            ),
            "rename-tree": UserCommand(
                name="rename-tree",
                description="Rename the current tree.",
                inputs=[
                    UserCommandInput("new_name", "Enter new tree name", required=True),
                ],
                handler=self._handle_rename_tree,
            ),
            "tree-info": UserCommand(
                name="tree-info",
                description="Show current tree information.",
                inputs=[],
                handler=self._handle_tree_info,
            ),
            "quit": UserCommand(
                name="quit",
                description="Exit the application.",
                inputs=[],
                handler=self._handle_quit,
            ),
        }

    def get_commands(self) -> Dict[str, UserCommand]:
        """Get all registered commands"""
        return self._commands

    def get_command_list(self) -> List[tuple]:
        """Get command list as (name, description) tuples for UI"""
        return [(cmd.name, cmd.description) for cmd in self._commands.values()]

    async def collect_input_for_command(self, command_name: str) -> Dict[str, Any]:
        """Collect user input for a specific command"""
        command = self._commands.get(command_name)
        if not command:
            raise ValueError(f"Unknown command: {command_name}")

        inputs = {}
        for input_def in command.inputs:
            prompt = input_def.prompt
            if input_def.default:
                prompt += f" (default {input_def.default})"
            prompt += ": "

            value = await asyncio.to_thread(input, prompt)

            # Use default if empty and default exists
            if not value.strip() and input_def.default:
                value = input_def.default

            # Type conversion
            if input_def.input_type == "int":
                value = (
                    int(value)
                    if value
                    else (int(input_def.default) if input_def.default else 0)
                )
            elif input_def.input_type == "float":
                value = (
                    float(value)
                    if value
                    else (float(input_def.default) if input_def.default else 0.0)
                )

            inputs[input_def.name] = value

        return inputs

    async def execute_command(self, command_name: str) -> bool:
        """Execute a command by name, collecting inputs and calling handler"""
        command = self._commands.get(command_name)
        if not command:
            raise ValueError(f"Unknown command: {command_name}")

        inputs = await self.collect_input_for_command(command_name)
        return await command.handler(**inputs)

    # Command handlers - these are simple and stay in this file
    async def _handle_start(self, depth: int = 3) -> bool:
        # No topic parameter - will use tree's topic automatically
        await self.controller.start_tree(None, depth)
        return False

    async def _handle_build(self, node_id: str, depth: int = 3) -> bool:
        await self.controller.build_tree(node_id, depth)
        return False

    async def _handle_expand(self, node_id: str) -> bool:
        await self.controller.expand_node(int(node_id))
        return False

    async def _handle_submit(self, argument: str, category: str) -> bool:
        await self.controller.submit_argument(argument, category)
        return False

    async def _handle_generate(self, node_id: str, num_arguments: int = 4) -> bool:
        await self.controller.generate_arguments(node_id, num_arguments)
        return False

    async def _handle_evaluate(self, node_id: int) -> bool:
        await self.controller.evaluate_node(node_id)
        return False

    async def _handle_load(self, file_path: str) -> bool:
        await self.controller.load_file(file_path)
        return False

    async def _handle_list(self) -> bool:
        await self.controller.list_nodes()
        return False

    async def _handle_path(self) -> bool:
        await self.controller.show_optimal_path()
        return False

    async def _handle_reset(self) -> bool:
        await self.controller.reset_tree()
        return False

    async def _handle_prune(self, threshold: str = "0.6") -> bool:
        from config.tree_config import tree_config

        try:
            threshold_float = float(threshold)

            # Validate against config bounds
            if threshold_float < tree_config.MIN_PRUNE_THRESHOLD:
                logger.error(
                    f"Threshold too low. Minimum: {tree_config.MIN_PRUNE_THRESHOLD}"
                )
                return False
            if threshold_float > tree_config.MAX_PRUNE_THRESHOLD:
                logger.error(
                    f"Threshold too high. Maximum: {tree_config.MAX_PRUNE_THRESHOLD}"
                )
                return False

            # Show what will happen before pruning
            logger.info(
                f"🌳 Pruning branches with path scores below {threshold_float:.2f}"
            )
            logger.info(
                "   This removes nodes where the BEST possible path averages below threshold"
            )
            logger.info(
                "   (Preserves promising branches even if current node is low-scored)"
            )

            await self.controller.prune_tree(threshold_float)

        except ValueError:
            logger.error(
                f"Invalid threshold: '{threshold}'. Please enter a number between "
                f"{tree_config.MIN_PRUNE_THRESHOLD} and {tree_config.MAX_PRUNE_THRESHOLD}"
            )
        return False

    # Tree Management Command Handlers
    async def _handle_create_tree(
        self, name: str, topic: str, description: str = None
    ) -> bool:
        await self.controller.create_tree(name, topic, description)
        return False

    async def _handle_switch_tree(self) -> bool:
        await self.controller.switch_tree_interactive()
        return False

    async def _handle_list_trees(self) -> bool:
        await self.controller.list_trees()
        return False

    async def _handle_delete_tree(self) -> bool:
        await self.controller.delete_tree_interactive()
        return False

    async def _handle_rename_tree(self, new_name: str) -> bool:
        await self.controller.rename_current_tree(new_name)
        return False

    async def _handle_tree_info(self) -> bool:
        await self.controller.show_current_tree_info()
        return False

    async def _handle_quit(self) -> bool:
        self.controller.quit_event.set()
        return True  # Signal to quit
