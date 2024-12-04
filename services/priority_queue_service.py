import heapq
from typing import Any, Dict, List

from config import priority_queue_config
from utils.dependency_registry import dependency_registry
from utils.logger import logger
from utils.state_saver import StateSaver


class PriorityQueueService:
    def __init__(self):
        self.queue = []
        self.entry_finder: Dict[str, Any] = {}
        self.REMOVED = "<removed-task>"
        self.counter = 0
        self.state_saver = StateSaver()
        logger.info("PriorityQueueService initialized")

    def add_node(self, node: Dict[str, Any], priority: str = "MEDIUM"):
        if priority not in priority_queue_config.PRIORITY_LEVELS:
            raise ValueError(
                f"Invalid priority level. Must be one of {list(priority_queue_config.PRIORITY_LEVELS.keys())}"
            )

        priority_value = priority_queue_config.PRIORITY_LEVELS[priority]
        node_id = str(node["id"])

        if node_id in self.entry_finder:
            self.remove_node(node_id)

        # Ensure node has required fields
        node_dict = {
            "id": node_id,
            "argument": node["argument"],
            "evaluation": node["evaluation"],
            "category": node["category"],
            "parent": node.get("parent", -1),
            "depth": node.get("depth", 0),
            "children": node.get("children", []),
        }

        entry = [priority_value, self.counter, node_dict]
        self.entry_finder[node_id] = entry
        heapq.heappush(self.queue, entry)
        self.counter += 1

        tree = dependency_registry.get("debate_tree_subject")
        tree.debate_tree = self.entry_finder

        logger.debug(f"Added node {node_id} with priority {priority}")

        # Save state after adding node
        self.state_saver.save_node_state(self.entry_finder, "node_add")

        # Update parent's children list if parent exists
        parent_id = str(node.get("parent", -1))
        if parent_id != "-1":
            parent_entry = self.entry_finder.get(parent_id)
            if parent_entry:
                parent_entry[2]["children"].append(node_id)

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

    # Allows for new nodes to be unique when they enter the queue
    def get_unique_id(self):
        return self.counter
