"""
TODO: This module...
"""

from config.environment import environment_config
from features.argument_generation.argument_generation_service import (
    ArgumentGenerationService,
)
from utils.dependency_registry import DependencyRegistry
from utils.logger import logger


class ArgumentGenerationInjector:
    def __init__(self, registry: DependencyRegistry):
        """TODO: Add Simple Docstring"""
        self.registry = registry

    def inject(self):
        """TODO: Add Simple Docstring"""
        logger.debug("Injecting argument generation services")

        model_factory = self.registry.get("model_factory")

        generation_model_name = environment_config.GENERATION_MODEL
        generation_model = model_factory.get_model(generation_model_name)

        if not generation_model:
            raise ValueError(
                f"Generation model '{generation_model_name}' is not enabled or available. "
                "Please check your ENABLED_LLMS configuration."
            )

        argument_generation_service = ArgumentGenerationService(generation_model)
        self.registry.register(
            "argument_generation_service", argument_generation_service
        )
        logger.info(
            f"Argument generation services injected successfully using {type(generation_model).__name__}"
        )
