"""
TODO: This module...
"""

from visualization.node_score_display import NodeScoreDisplay
from visualization.renderer_factory import RendererFactory
from visualization.tree_renderer import TreeRenderer
from utils.dependency_registry import DependencyRegistry
from utils.logger import logger


class VisualizationInjector:
    def __init__(self, registry: DependencyRegistry, renderer_type: str):
        """TODO: Add Simple Docstring"""
        self.registry = registry
        self.renderer_type = renderer_type

    def inject(self):
        """TODO: Add Simple Docstring"""
        logger.info(
            f"Injecting visualization services with {self.renderer_type} renderer"
        )

        repository = self.registry.get("tree_repository")

        node_score_display = NodeScoreDisplay(repository)
        self.registry.register("node_score_display", node_score_display)

        # The factory creates the specific renderer (e.g., Pygame, Plotly)
        specific_renderer = RendererFactory.create_renderer(
            self.renderer_type,
            self.registry.get(
                "multi_tree_state_service"
            ),  # Still needed for some renderers' interactive state
            repository=repository,
        )

        # The TreeRenderer is a manager that uses the specific renderer
        tree_renderer = TreeRenderer(specific_renderer, repository)

        self.registry.register("renderer", tree_renderer)

        logger.info(
            f"Visualization services injected successfully with {self.renderer_type} renderer"
        )
