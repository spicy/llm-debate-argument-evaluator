"""
TODO: This module...
"""

from typing import Any


from commands.create_root_node_command import CreateRootNodeCommand
from commands.create_node_command import CreateNodeCommand
from commands.evaluate_node_command import EvaluateNodeCommand
from commands.expand_node_command import ExpandNodeCommand
from commands.generate_tree_arguments_command import (
    GenerateTreeArgumentsCommand,
)
from commands.load_tree_from_file_command import LoadTreeFromFileCommand
from commands.load_tree_from_repository_command import LoadTreeFromRepositoryCommand
from commands.start_new_tree_command import StartNewTreeCommand
from commands.submit_argument_command import SubmitArgumentCommand
from commands.reset_tree_command import ResetTreeCommand
from commands.build_tree_command import BuildTreeCommand
from commands.show_optimal_path_command import ShowOptimalPathCommand
from commands.prune_tree_command import PruneTreeCommand
from commands.tree_management import (
    CreateTreeCommand,
    SwitchTreeCommand,
    ListTreesCommand,
    DeleteTreeCommand,
    RenameTreeCommand,
)
from features.tree.multi_tree_state_service import MultiTreeStateService
from features.tree.traversal_logic import TraversalLogic
from utils.dependency_registry import DependencyRegistry
from utils.logger import logger


class CommandInjector:
    def __init__(self, registry: DependencyRegistry):
        """Initializes the command injector."""
        self.registry = registry

    def inject(self):
        """Injects and registers all command services."""
        logger.debug("Injecting command services")

        # Get core services from the registry
        state_service = self.registry.get("multi_tree_state_service")
        repository = self.registry.get("tree_repository")
        tree_metadata_repo = self.registry.get("tree_metadata_repository")
        tree_selection_service = self.registry.get("tree_selection_service")
        arg_gen_service = self.registry.get("argument_generation_service")
        async_service = self.registry.get("async_processing_service")
        traversal_logic = self.registry.get("traversal_logic")
        evaluation_service = self.registry.get("evaluation_service")
        score_aggregator_service = self.registry.get("score_aggregator_service")

        # Register commands starting with the ones that have no other command dependencies
        create_root_command = CreateRootNodeCommand(state_service, tree_metadata_repo)
        self.registry.register("create_root_node_command", create_root_command)

        generate_args_command = GenerateTreeArgumentsCommand(
            arg_gen_service, async_service
        )
        self.registry.register("generate_tree_arguments_command", generate_args_command)

        self.registry.register(
            "load_nodes_from_file_command", LoadTreeFromFileCommand(state_service)
        )
        self.registry.register(
            "load_tree_command", LoadTreeFromRepositoryCommand(state_service)
        )
        self.registry.register("reset_tree_command", ResetTreeCommand(state_service))

        show_optimal_path_command = ShowOptimalPathCommand(
            tree_state_service=state_service, traversal_logic=traversal_logic
        )
        self.registry.register("show_optimal_path_command", show_optimal_path_command)

        # Register prune command
        prune_tree_command = PruneTreeCommand(state_service, repository)
        self.registry.register("prune_tree_command", prune_tree_command)

        # Register the shared node creation command
        create_node_command = CreateNodeCommand(
            evaluation_service=evaluation_service,
            score_aggregator_service=score_aggregator_service,
            async_processing_service=async_service,
            tree_state_service=state_service,
        )
        self.registry.register("create_node_command", create_node_command)

        # Register commands that depend on other commands
        expand_node_command = ExpandNodeCommand(
            generate_tree_arguments_command=generate_args_command,
            create_node_command=create_node_command,
            tree_state_service=state_service,
        )
        self.registry.register("expand_node_command", expand_node_command)

        evaluate_node_command = EvaluateNodeCommand(
            evaluation_service=evaluation_service,
            score_aggregator_service=score_aggregator_service,
            state_service=state_service,
        )
        self.registry.register("evaluate_node_command", evaluate_node_command)

        # BuildTreeCommand will be injected with the controller's expand function in the controller
        build_tree_command = BuildTreeCommand(
            traversal_logic=traversal_logic,
        )
        self.registry.register("build_tree_command", build_tree_command)

        start_new_tree_command = StartNewTreeCommand(
            create_root_command=create_root_command,
            expand_node_command=expand_node_command,
            evaluate_tree_command=evaluate_node_command,
            traverse_command=build_tree_command,
            async_processing_service=async_service,
            tree_state_service=state_service,
        )
        self.registry.register("start_new_tree_command", start_new_tree_command)

        submit_argument_command = SubmitArgumentCommand(
            create_node_command=create_node_command,
            tree_state_service=state_service,
        )
        self.registry.register("submit_argument_command", submit_argument_command)

        # Register tree management commands
        create_tree_command = CreateTreeCommand(tree_selection_service)
        self.registry.register("create_tree_command", create_tree_command)

        switch_tree_command = SwitchTreeCommand(tree_selection_service)
        self.registry.register("switch_tree_command", switch_tree_command)

        list_trees_command = ListTreesCommand(tree_selection_service)
        self.registry.register("list_trees_command", list_trees_command)

        delete_tree_command = DeleteTreeCommand(tree_selection_service)
        self.registry.register("delete_tree_command", delete_tree_command)

        rename_tree_command = RenameTreeCommand(tree_selection_service)
        self.registry.register("rename_tree_command", rename_tree_command)

        logger.info("All command services injected successfully")
