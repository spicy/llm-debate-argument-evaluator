"""
TODO: This module...
"""

from commands.command_injector import CommandInjector
from features.argument_generation.injector import ArgumentGenerationInjector
from features.tree.injector import TreeInjector
from features.evaluation.injector import EvaluationInjector
from infrastructure.injector import InfrastructureInjector
from utils.dependency_registry import DependencyRegistry
from utils.logger import log_execution_time, logger
from visualization.visualization_injector import VisualizationInjector
from infrastructure.database.supabase_service import SupabaseService
from features.tree.tree_repository import TreeRepository


class DependencyInjector:
    def __init__(self):
        """TODO: Add Simple Docstring"""
        self.registry = DependencyRegistry()
        logger.debug("DependencyInjector initialized")

    @log_execution_time
    def initialize_dependencies(self, renderer_type: str):
        """TODO: Add Simple Docstring"""
        logger.debug("Initializing dependencies")

        # Infrastructure Layer
        infra_injector = InfrastructureInjector(self.registry)
        infra_injector.inject()

        # Supabase and Repository
        supabase_service = SupabaseService()
        self.registry.register("supabase_service", supabase_service)

        tree_repository = TreeRepository(supabase_service)
        self.registry.register("tree_repository", tree_repository)

        # Feature Layer
        eval_injector = EvaluationInjector(self.registry)
        eval_injector.inject()

        arg_gen_injector = ArgumentGenerationInjector(self.registry)
        arg_gen_injector.inject()

        tree_injector = TreeInjector(self.registry)
        tree_injector.inject()

        # Visualization Layer
        vis_injector = VisualizationInjector(self.registry, renderer_type)
        vis_injector.inject()

        # Command Layer
        command_injector = CommandInjector(self.registry)
        command_injector.inject()

        logger.info("Dependencies initialized successfully")
