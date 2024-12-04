from typing import Any, Dict

from config.debate_traversal_config import debate_traversal_config
from config.debate_tree_config import debate_tree_config
from services.priority_queue_service import PriorityQueueService
from utils.logger import logger


class TraversalLogic:
    def __init__(self, priority_queue_service: PriorityQueueService):
        self.priority_queue_service = priority_queue_service
        self.visited_nodes: Dict[str, Any] = {}
        logger.info("TraversalLogic initialized")

    async def traverse(
        self,
        root_node_id: str,
        get_node_func,
        expand_node_func,
        evaluate_node_func,
        max_depth: int = debate_tree_config.MAX_TREE_DEPTH,
    ):
        while not self.priority_queue_service.is_empty():
            current_node = self.priority_queue_service.pop_node()
            current_node_id = current_node["id"]

            if current_node_id in self.visited_nodes:
                continue

            if current_node["depth"] >= max_depth:
                logger.debug(
                    f"Reached max depth {max_depth} for node {current_node_id}"
                )
                continue

            self.visited_nodes[current_node_id] = current_node
            logger.debug(f"Visiting node {current_node_id}")

            existing_children = self.priority_queue_service.get_children(
                current_node_id
            )

            if len(existing_children) < debate_tree_config.MAX_CHILDREN_PER_NODE:
                try:
                    new_nodes = await expand_node_func(current_node_id)
                    for new_node in new_nodes:
                        evaluation = await evaluate_node_func(new_node["id"])
                        priority = self._determine_priority(evaluation)
                        new_node["depth"] = current_node["depth"] + 1
                        self.priority_queue_service.add_node(new_node, priority)
                except Exception as e:
                    logger.error(f"Error expanding node {current_node_id}: {str(e)}")

            yield current_node

    def _determine_priority(self, evaluation: dict) -> str:
        """
        Determine priority level based on evaluation score
        """
        if not evaluation:
            return "MEDIUM"

        avg_score = sum(evaluation.values()) / len(evaluation) if evaluation else 0.0

        if avg_score >= debate_traversal_config.HIGH_PRIORITY_THRESHOLD:
            return "HIGH"
        elif avg_score <= debate_traversal_config.LOW_PRIORITY_THRESHOLD:
            return "LOW"
        return "MEDIUM"
