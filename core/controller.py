"""
TODO: This module...
"""

from typing import List, Dict, Any
from core.user_interactions import UserInteractions

from utils.logger import log_execution_time, logger


class Controller:
    def __init__(self, injector, quit_event, user_interactions):
        """TODO: Add Simple Docstring"""
        self.injector = injector
        self.user_interactions = user_interactions
        self.quit_event = quit_event

    @log_execution_time
    async def start(self):
        """TODO: Add Simple Docstring"""
        await self.user_interactions.main_loop()

    @log_execution_time
    async def create_root_node(self, topic: str) -> str:
        """Creates the root node for a tree"""
        logger.info(f"Creating root node for topic: {topic}")
        create_root_command = self.injector.get("create_root_node_command")
        return await create_root_command.execute(topic)

    @log_execution_time
    async def expand_node(self, node_id: int) -> List[Dict[str, Any]]:
        logger.info(f"Controller.expand_node called for node: {node_id}")
        expand_node_command = self.injector.get("expand_node_command")
        new_nodes = await expand_node_command.execute(node_id)

        # Auto-update optimal path after adding new nodes
        if new_nodes:
            logger.info(
                f"Found {len(new_nodes)} new nodes, triggering auto-update of optimal path"
            )
            await self._auto_update_optimal_path("after node expansion")
        else:
            logger.info("No new nodes created, skipping optimal path update")

        # Return the new nodes for use by traversal logic (ensure it's always a list)
        return new_nodes or []

    @log_execution_time
    async def evaluate_node(self, node_id: int):
        """Evaluates a single node in the tree"""
        logger.info(f"Starting evaluation for node: {node_id}")
        evaluate_command = self.injector.get("evaluate_node_command")
        await evaluate_command.execute(node_id)

        # Auto-update optimal path after score changes
        await self._auto_update_optimal_path("after node evaluation")

    @log_execution_time
    async def build_tree(self, root_node_id: str, max_depth: int):
        """Builds out an existing tree from a root node"""
        logger.info(f"Starting tree build process from node: {root_node_id}")
        build_command = self.injector.get("build_tree_command")

        # Inject the controller's expand_node method to ensure auto-updates
        logger.info("Injecting controller's expand_node method into build command")
        build_command.expand_node_func = self.expand_node

        await build_command.execute(root_node_id, max_depth)

        # Auto-update optimal path after tree building
        await self._auto_update_optimal_path("after tree building")

    @log_execution_time
    async def submit_argument(self, argument, category):
        logger.info(f"Submitting argument in category: {category}")
        submit_argument_command = self.injector.get("submit_argument_command")
        new_node = await submit_argument_command.execute(argument, category)

        # Auto-update optimal path after adding new argument
        if new_node:
            await self._auto_update_optimal_path("after argument submission")

    @log_execution_time
    async def generate_arguments(self, node_id: str, num_arguments: int):
        logger.info(f"Generating arguments for node: {node_id}")

        tree_state_service = self.injector.get("multi_tree_state_service")
        node = tree_state_service.get_node(node_id)
        if not node:
            logger.warning(f"Node with ID '{node_id}' not found.")
            logger.info(f"Node with ID '{node_id}' not found.")
            return

        node_argument = node.get("argument", "")
        category = node.get("category", "general")

        generate_command = self.injector.get("generate_tree_arguments_command")
        generated_arguments = await generate_command.execute(
            node_argument, category, num_arguments
        )

        if generated_arguments:
            logger.info(f"--- Generated Arguments for Node {node_id} ---")
            for arg in generated_arguments:
                logger.info(f"- Type: {arg['type']}, Argument: {arg['text']}")
            logger.info("-------------------------------------------\n")
        else:
            logger.info("Could not generate arguments.")

    @log_execution_time
    async def load_file(self, file_path: str):
        logger.info(f"Loading arguments from file: {file_path}")
        load_file_command = self.injector.get("load_nodes_from_file_command")
        await load_file_command.execute(file_path)

    @log_execution_time
    async def load_tree(self):
        """Loads an existing tree from the repository."""
        logger.info("Loading existing tree from repository.")
        load_tree_command = self.injector.get("load_tree_command")
        await load_tree_command.execute()

    @log_execution_time
    async def start_tree(self, topic: str = None, max_depth: int = 3):
        """Starts the complete tree process"""
        if topic:
            logger.info(f"Running complete tree process for topic: {topic}")
        else:
            logger.info("Running complete tree process using tree's default topic")
        run_command = self.injector.get("start_new_tree_command")
        return await run_command.execute(topic, max_depth)

    @log_execution_time
    async def list_nodes(self):
        """Lists all nodes in the tree from the in-memory state."""
        logger.info("Listing all nodes")
        state_service = self.injector.get("multi_tree_state_service")
        all_nodes_list = state_service.get_all_nodes()
        if not all_nodes_list:
            logger.info("No nodes in the tree.")
            return

        logger.info("\n--- All Nodes in tree ---")
        for node_data in sorted(all_nodes_list, key=lambda x: x["id"]):
            evaluation = node_data.get("evaluation", {})

            # Safely extract average score
            if isinstance(evaluation, dict):
                avg_score = evaluation.get("average", 0.0)
            elif evaluation is not None:
                avg_score = float(evaluation)
            else:
                avg_score = 0.0

            # Ensure all values are safe for formatting
            argument = node_data.get("argument") or "N/A"
            parent = node_data.get("parent_id") or "N/A"
            depth = node_data.get("depth")
            depth = depth if depth is not None else "N/A"
            arg_type = node_data.get("argument_type") or "N/A"
            visits = node_data.get("visits", 0)
            wins = node_data.get("wins", 0.0)

            # Calculate win rate safely
            win_rate = (wins / visits) if visits > 0 else 0.0

            logger.info(
                f"ID: {node_data['id']} | Parent: {parent} | Depth: {depth} | "
                f"Type: {str(arg_type).upper():<10} | Score: {avg_score:.2f} | "
                f"Visits: {visits} | Win Rate: {win_rate:.2f} | "
                f"Argument: {argument[:100]}..."
            )
        logger.info("---------------------------------\n")

    @log_execution_time
    async def show_optimal_path(self):
        """Shows the current optimal path in the tree."""
        logger.info("User requested to show the optimal path.")
        show_path_command = self.injector.get("show_optimal_path_command")
        await show_path_command.execute()

    @log_execution_time
    async def reset_tree(self):
        """Resets the entire tree."""
        logger.info("User requested to reset the tree.")
        reset_command = self.injector.get("reset_tree_command")
        await reset_command.execute()

    async def _auto_update_optimal_path(self, context: str = ""):
        """Automatically recalculate and display optimal path after tree changes."""
        try:
            logger.info(f"Auto-updating optimal path {context}")
            show_path_command = self.injector.get("show_optimal_path_command")
            await show_path_command.execute()
            logger.info(f"Optimal path auto-update completed {context}")
        except Exception as e:
            logger.warning(f"Failed to auto-update optimal path {context}: {e}")

    @log_execution_time
    async def prune_tree(self, threshold: float):
        """Prune low-quality branches from the tree."""
        logger.info(f"User requested to prune tree with threshold {threshold:.2f}")
        prune_command = self.injector.get("prune_tree_command")
        removed_count = await prune_command.execute(threshold)
        logger.info(f"Pruning completed: {removed_count} nodes removed")

        # Auto-update optimal path after structural changes
        if removed_count > 0:
            await self._auto_update_optimal_path("after pruning")

    # Tree Management Methods
    @log_execution_time
    async def create_tree(self, name: str, topic: str, description: str = None):
        """Create a new debate tree."""
        logger.info(f"User requested to create new tree: '{name}'")
        create_tree_command = self.injector.get("create_tree_command")
        await create_tree_command.execute(name, topic, description, switch_to_tree=True)

    @log_execution_time
    async def switch_tree_interactive(self):
        """Switch to a different tree with interactive selection."""
        logger.info("User requested to switch trees (interactive)")
        switch_tree_command = self.injector.get("switch_tree_command")
        await switch_tree_command.execute_interactive()

    @log_execution_time
    async def list_trees(self):
        """List all available trees with detailed information."""
        logger.info("User requested to list trees")
        list_trees_command = self.injector.get("list_trees_command")
        await list_trees_command.execute(detailed=True)

    @log_execution_time
    async def delete_tree_interactive(self):
        """Delete a tree with interactive selection and confirmation."""
        logger.info("User requested to delete a tree (interactive)")
        delete_tree_command = self.injector.get("delete_tree_command")
        await delete_tree_command.execute_interactive()

    @log_execution_time
    async def rename_current_tree(self, new_name: str):
        """Rename the currently selected tree."""
        logger.info(f"User requested to rename current tree to: '{new_name}'")
        rename_tree_command = self.injector.get("rename_tree_command")
        await rename_tree_command.execute_current_tree(new_name)

    @log_execution_time
    async def show_current_tree_info(self):
        """Show information about the currently selected tree."""
        logger.info("User requested current tree information")
        switch_tree_command = self.injector.get("switch_tree_command")
        switch_tree_command.show_current_tree()

    async def ensure_tree_selected(self) -> bool:
        """Ensure a tree is selected, prompting user if needed."""
        switch_tree_command = self.injector.get("switch_tree_command")
        return await switch_tree_command.ensure_tree_selected()
