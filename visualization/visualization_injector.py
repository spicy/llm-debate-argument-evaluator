from utils.logger import logger

from .node_expansion_handler import NodeExpansionHandler
from .node_score_display import NodeScoreDisplay
from .observer import DebateTreeSubject
from .tree_renderer import TreeRenderer


class VisualizationInjector:
    @staticmethod
    def inject_visualization_services(registry):
        logger.info("Injecting visualization services")

        debate_tree_subject = DebateTreeSubject()
        tree_renderer = TreeRenderer(debate_tree_subject)
        node_expansion_handler = NodeExpansionHandler(debate_tree_subject)
        node_score_display = NodeScoreDisplay(debate_tree_subject)

        registry.register("debate_tree_subject", debate_tree_subject)
        registry.register("tree_renderer", tree_renderer)
        registry.register("node_expansion_handler", node_expansion_handler)
        registry.register("node_score_display", node_score_display)

        logger.info("Visualization services injected successfully")
