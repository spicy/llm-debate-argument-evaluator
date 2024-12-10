from utils.logger import logger

from .node_score_display import NodeScoreDisplay
from .tree_renderer import TreeRenderer


class VisualizationInjector:
    @staticmethod
    def inject_visualization_services(registry):
        logger.info("Injecting visualization services")

        # Get priority queue service from registry
        priority_queue_service = registry.get("priority_queue_service")

        # Create visualization components using priority queue as subject
        node_score_display = NodeScoreDisplay(priority_queue_service)
        tree_renderer = TreeRenderer(priority_queue_service)

        # Register visualization components
        registry.register("node_score_display", node_score_display)
        registry.register("tree_renderer", tree_renderer)

        logger.info("Visualization services injected successfully")
