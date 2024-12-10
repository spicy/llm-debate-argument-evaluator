from utils.logger import logger

from .node_score_display import NodeScoreDisplay
from .priority_queue_service import PriorityQueueService
from .tree_renderer import TreeRenderer


class VisualizationInjector:
    @staticmethod
    def inject_visualization_services(registry):
        logger.info("Injecting visualization services")

        # Use PriorityQueueService as the subject
        priority_queue_service = PriorityQueueService()

        # Create visualization components using priority queue as subject
        node_score_display = NodeScoreDisplay(priority_queue_service)
        tree_renderer = TreeRenderer(priority_queue_service)

        # Register visualization components
        registry.register("priority_queue_service", priority_queue_service)
        registry.register("node_score_display", node_score_display)
        registry.register("tree_renderer", tree_renderer)

        logger.info("Visualization services injected successfully")
