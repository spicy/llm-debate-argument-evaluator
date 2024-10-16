from commands.command_injector import CommandInjector
from debate_traversal.traversal_injector import TraversalInjector
from evaluation.evaluation_injector import EvaluationInjector
from services.argument_generation_injector import ArgumentGenerationInjector
from services.services_injector import ServicesInjector
from utils.dependency_registry import dependency_registry
from utils.logger import log_execution_time, logger
from visualization.visualization_injector import VisualizationInjector


class DependencyInjector:
    def __init__(self):
        self.registry = dependency_registry
        logger.debug("DependencyInjector initialized")

    def register(self, name, dependency):
        self.registry.register(name, dependency)

    def get(self, name):
        return self.registry.get(name)

    @log_execution_time
    def initialize_dependencies(self):
        logger.debug("Initializing dependencies")

        # Inject services
        ServicesInjector.inject_services(self.registry)

        # Inject evaluation services
        EvaluationInjector.inject_evaluation_services(self.registry)

        # Inject argument generation services
        ArgumentGenerationInjector.inject_argument_generation_services(self.registry)

        # Initialize visualization components
        VisualizationInjector.inject_visualization_services(self.registry)

        # Initialize traversal services
        TraversalInjector.inject_traversal_services(self.registry)

        # Initialize and register commands
        CommandInjector.inject_commands(self.registry)

        logger.info("Dependencies initialized successfully")

    def clear_dependencies(self):
        self.registry.clear()
        logger.debug("Dependencies cleared")
