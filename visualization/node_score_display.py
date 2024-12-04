from typing import Any, Dict

from utils.logger import logger
from visualization.observer import DebateTreeSubject, Observer
from services.priority_queue_service import PriorityQueueService


class NodeScoreDisplay(Observer):
    def __init__(self, debate_tree_subject: DebateTreeSubject, priority_queue_manager: PriorityQueueService):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)
        self.priority_queue_manager = priority_queue_manager

    def update(self, subject):
        self.display_scores(subject.debate_tree)

    def display_scores(self, debate_tree: Dict[str, Any]):
        logger.info("Displaying nodes from prioity scores")

        top_node = self.priority_queue_manager.get_top_node()
        score = -top_node[0]
        color = self._score_to_color(score)
        logger.info(f"Top Node: {top_node[1]}: Score = {score}, Color = {color}")

        for node_data in self.priority_queue_manager.queue:
            score = node_data[2].get("evaluation", 0)
            color = self._score_to_color(score)
            logger.info(f"Node {node_data[1]}: Score = {score:.2f}, Color = {color}")

    def _score_to_color(self, score: float):
        r = max(0, min(255, int(255 * (1 - score))))
        g = max(0, min(255, int(255 * score)))
        return f"#{r:02x}{g:02x}00"
