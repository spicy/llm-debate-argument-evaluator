from typing import Any, Dict, List

from config import debate_traversal_config, debate_tree_config
from debate_traversal.priority_queue_manager import PriorityQueueManager
from utils.logger import logger


class TraversalLogic:
    def __init__(self, priority_queue_manager: PriorityQueueManager):
        self.priority_queue_manager = priority_queue_manager
        self.visited_nodes: Dict[str, Any] = {}
        logger.info("TraversalLogic initialized")

    async def traverse(
        self, root_node_id: str, get_node_func, expand_node_func, evaluate_node_func
    ):
        self.priority_queue_manager.add_node(root_node_id, "HIGH")

        while not self.priority_queue_manager.is_empty():
            current_node_id = self.priority_queue_manager.pop_node()
            current_node = get_node_func(current_node_id)

            if (
                current_node_id in self.visited_nodes
                or current_node["depth"] >= debate_tree_config.MAX_TREE_DEPTH
            ):
                continue

            self.visited_nodes[current_node_id] = current_node
            logger.debug(f"Visiting node {current_node_id}")

            if len(current_node["children"]) < debate_tree_config.MAX_CHILDREN_PER_NODE:
                new_nodes = await expand_node_func(current_node_id)
                for new_node in new_nodes:
                    evaluation = await evaluate_node_func(new_node["id"])
                    priority = self._determine_priority(evaluation)
                    self.priority_queue_manager.add_node(new_node["id"], priority)

            yield current_node

    def _determine_priority(self, evaluation: Dict[str, float]) -> str:
        avg_score = sum(evaluation.values()) / len(evaluation)
        if avg_score >= debate_traversal_config.HIGH_PRIORITY_THRESHOLD:
            return "HIGH"
        elif avg_score <= debate_traversal_config.LOW_PRIORITY_THRESHOLD:
            return "LOW"
        else:
            return "MEDIUM"
