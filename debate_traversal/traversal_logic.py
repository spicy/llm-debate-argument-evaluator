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
        """Traverse the debate tree starting from root_node_id"""
        try:
            root_node = get_node_func(root_node_id)
            if not root_node:
                logger.error(f"Root node {root_node_id} not found")
                return

            # Initialize root node in priority queue if not visited
            if str(root_node["id"]) not in self.visited_nodes:
                evaluation = await evaluate_node_func(root_node_id)
                priority = self._determine_priority(evaluation)
                self.priority_queue_service.add_node(root_node, priority)
                logger.debug(f"Added root node {root_node_id} to priority queue")

            while True:
                try:
                    if self.priority_queue_service.is_empty():
                        logger.debug("Priority queue is empty, ending traversal")
                        break

                    current_node = self.priority_queue_service.pop_node()
                    if not current_node:
                        continue

                    current_node_id = str(current_node["id"])
                    if current_node_id in self.visited_nodes:
                        continue

                    # Check depth before processing
                    if current_node["depth"] >= max_depth:
                        logger.debug(
                            f"Reached max depth {max_depth} for node {current_node_id}"
                        )
                        self.visited_nodes[current_node_id] = current_node
                        yield current_node
                        continue

                    self.visited_nodes[current_node_id] = current_node
                    logger.debug(f"Visiting node {current_node_id}")

                    # Expand current node
                    new_nodes = await expand_node_func(current_node_id)
                    if new_nodes:
                        for new_node in new_nodes:
                            new_node_id = str(new_node["id"])
                            if new_node_id not in self.visited_nodes:
                                evaluation = await evaluate_node_func(new_node_id)
                                priority = self._determine_priority(evaluation)
                                new_node["depth"] = current_node["depth"] + 1
                                self.priority_queue_service.add_node(new_node, priority)
                                logger.debug(
                                    f"Added new node {new_node_id} with priority {priority}"
                                )

                    yield current_node

                except KeyError as e:
                    logger.error(f"Error during node processing: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Fatal error in traverse: {str(e)}")
            return

    def _determine_priority(self, evaluation: Any) -> str:
        """Determine priority based on evaluation score"""
        if isinstance(evaluation, dict):
            # If evaluation is a dict, use the average of scores
            score = sum(evaluation.values()) / len(evaluation) if evaluation else 0.5
        else:
            # If evaluation is a number, use it directly
            score = float(evaluation) if evaluation is not None else 0.5

        if score >= debate_traversal_config.HIGH_PRIORITY_THRESHOLD:
            return "HIGH"
        elif score <= debate_traversal_config.LOW_PRIORITY_THRESHOLD:
            return "LOW"
        return "MEDIUM"
