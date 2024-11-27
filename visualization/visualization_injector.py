from utils.logger import logger

from .node_score_display import NodeScoreDisplay
from .observer import DebateTreeSubject
from .modified_renderer import ModifiedRenderer


class VisualizationInjector:
    @staticmethod
    def inject_visualization_services(registry):
        logger.info("Injecting visualization services")

        debate_tree_subject = DebateTreeSubject()
        node_score_display = NodeScoreDisplay(debate_tree_subject)
        modified_renderer = ModifiedRenderer(debate_tree_subject)

        registry.register("debate_tree_subject", debate_tree_subject)
        registry.register("node_score_display", node_score_display)
        registry.register("modified_renderer", modified_renderer)

        logger.info("Visualization services injected successfully")
