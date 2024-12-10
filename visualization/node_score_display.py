from typing import Any, Dict

from services.priority_queue_service import PriorityQueueService
from utils.logger import logger
from visualization.observer import Observer


class NodeScoreDisplay(Observer):
    def __init__(self, priority_queue_service: PriorityQueueService):
        self.priority_queue_service = priority_queue_service
        self.priority_queue_service.attach(self)

    def update(self, subject):
        self.display_scores(subject.debate_tree)

    def display_scores(self, debate_tree: Dict[str, Any]):
        logger.info("Displaying node scores")
        for node_id, node_data in debate_tree.items():
            score = node_data.get("evaluation", 0)
            color = self._score_to_color(score)
            logger.info(f"Node {node_id}: Score = {score:.2f}, Color = {color}")

    def _score_to_color(self, score: float):
        r = max(0, min(255, int(255 * (1 - score))))
        g = max(0, min(255, int(255 * score)))
        return f"#{r:02x}{g:02x}00"
