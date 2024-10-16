from typing import Any, Dict

import matplotlib.pyplot as plt
import networkx as nx

from utils.logger import logger

from .observer import DebateTreeSubject, Observer


class TreeRenderer(Observer):
    def __init__(self, debate_tree_subject: DebateTreeSubject):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)
        self.G = nx.Graph()

    def update(self, subject):
        self.render_tree(subject.debate_tree)

    def render_tree(self, debate_tree: Dict[str, Any]):
        logger.info("Rendering debate tree")
        self.G.clear()
        for node_id, node_data in debate_tree.items():
            self.G.add_node(node_id)
            if node_data.get("parent"):
                self.G.add_edge(node_data["parent"], node_id)

        pos = nx.spring_layout(self.G)
        plt.figure(figsize=(12, 8))
        nx.draw(
            self.G,
            pos,
            with_labels=True,
            node_color=self._get_node_colors(debate_tree),
            node_size=self._get_node_sizes(debate_tree),
            font_size=8,
            font_weight="bold",
        )
        plt.title("Debate Tree Visualization")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig("debate_tree.png")
        plt.close()
        logger.info("Debate tree rendered and saved as 'debate_tree.png'")

    def _get_node_colors(self, debate_tree: Dict[str, Any]):
        return [
            self._score_to_color(node_data.get("score", 0))
            for node_data in debate_tree.values()
        ]

    def _get_node_sizes(self, debate_tree: Dict[str, Any]):
        return [
            1000 * node_data.get("score", 0.5) for node_data in debate_tree.values()
        ]

    def _score_to_color(self, score: float):
        r = max(0, min(255, int(255 * (1 - score))))
        g = max(0, min(255, int(255 * score)))
        return f"#{r:02x}{g:02x}00"
