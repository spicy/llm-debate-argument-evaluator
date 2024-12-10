from typing import Any, Dict, List

from config.debate_traversal_config import debate_traversal_config
from config.debate_tree_config import debate_tree_config
from services.interfaces.queue_service_interface import QueueServiceInterface
from utils.logger import logger


class TraversalLogic:
    def __init__(self, priority_queue_service: QueueServiceInterface):
        self.priority_queue_service = priority_queue_service
        self.visited_nodes: Dict[str, Any] = {}
        self.optimal_path: List[Dict[str, Any]] = []
        self.best_score = 0.0
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
                self._track_optimal_path(root_node)
                logger.debug(f"Added root node {root_node_id} to priority queue")

            while True:
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
                    self._track_optimal_path(current_node)
                    yield current_node
                    continue

                # Mark as visited before expansion
                self.visited_nodes[current_node_id] = current_node
                logger.debug(f"Visiting node {current_node_id}")

                # Expand current node and add children to priority queue
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

                self._track_optimal_path(current_node)
                yield current_node

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

    def _track_optimal_path(self, current_node: Dict[str, Any]) -> None:
        """Track the optimal path based on cumulative evaluation scores"""
        # Only track paths for leaf nodes (at max depth or with no children)
        if current_node["depth"] < debate_tree_config.MAX_TREE_DEPTH:
            children = self.priority_queue_service.get_children(str(current_node["id"]))
            if children and len(children) > 0:
                return

        # Build current path from current node to root
        path = []
        node = current_node
        total_score = 0

        while node:
            path.append(node)
            total_score += float(node.get("evaluation", 0))
            parent_id = node.get("parent")
            if parent_id == -1:  # Reached root
                break
            node = self.priority_queue_service.get_node(str(parent_id))
            if not node:  # Handle broken paths
                break

        # Update optimal path if this path has a better total score
        if total_score > self.best_score:
            self.best_score = total_score
            self.optimal_path = list(reversed(path))  # Store path from root to leaf
            logger.debug(
                f"New optimal path found with score {total_score}. "
                f"Path: {' -> '.join(str(n['id']) for n in self.optimal_path)}"
            )

    def print_optimal_path(self) -> None:
        """Print the optimal path through the debate tree using ASCII characters"""
        if not self.optimal_path:
            logger.info("No optimal path found")
            return

        logger.info("\nOptimal debate path (best scoring route):")
        for i, node in enumerate(self.optimal_path):
            indent = "  " * i
            score = node.get("evaluation", 0)
            logger.info(f"{indent}+- Node {node['id']} (Score: {score:.2f})")
            logger.info(f"{indent}|  Argument: {node['argument'][:100]}...")
