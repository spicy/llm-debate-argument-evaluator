import heapq
from typing import Any, Dict, List

from config.priority_queue_config import priority_queue_config
from utils.logger import logger
from utils.state_saver import StateSaver


class PriorityQueueService:
    def __init__(self):
        self.queue = []
        self.entry_finder = {}
        self.REMOVED = "<removed>"
        self.counter = 0
        self.state_saver = StateSaver()
        self.PRIORITY_LEVELS = priority_queue_config.PRIORITY_LEVELS
        logger.info("PriorityQueueService initialized")

    def add_node(self, node: Dict[str, Any], priority_level: str = "MEDIUM"):
        """
        Add a node to the priority queue
        """
        node_id = str(node["id"])
        priority = self.PRIORITY_LEVELS.get(
            priority_level, self.PRIORITY_LEVELS["MEDIUM"]
        )

        if node_id in self.entry_finder:
            self.remove_node(node_id)

        count = self.counter
        self.counter += 1

        entry = [
            -priority,
            count,
            node,
        ]  # Note the negative priority for max-heap behavior
        self.entry_finder[node_id] = entry
        heapq.heappush(self.queue, entry)
        logger.debug(f"Added node {node_id} with priority {priority_level}")

        # Save state after adding node
        self.state_saver.save_node_state(self.entry_finder, "node_add")

    def remove_node(self, node_id):
        entry = self.entry_finder.pop(node_id)
        entry[-1] = self.REMOVED
        logger.debug(f"Removed node {node_id}")

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Get node data from entry_finder"""
        entry = self.entry_finder.get(str(node_id))
        if not entry:
            return None
        return entry[2]  # Return the node_dict part

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all children of a node"""
        return [
            entry[2]
            for entry in self.entry_finder.values()
            if entry[2].get("parent") == str(parent_id)
        ]

    def pop_node(self):
        while self.queue:
            priority, count, node = heapq.heappop(self.queue)
            if node is not self.REMOVED:
                del self.entry_finder[node["id"]]
                logger.debug(f"Popped node {node['id']} with priority {priority}")
                return node
        logger.error("Attempted to pop from an empty priority queue")
        raise KeyError("pop from an empty priority queue")

    def is_empty(self):
        """Check if the priority queue is empty"""
        return len(self.queue) == 0

    def get_unique_id(self):
        """Get a unique ID for new nodes"""
        unique_id = self.counter
        self.counter += 1
        return unique_id

    def get_all_nodes(self) -> Dict[str, Any]:
        """Get all nodes in the priority queue"""
        return {
            node_id: entry[2]
            for node_id, entry in self.entry_finder.items()
            if entry[2] is not self.REMOVED
        }
