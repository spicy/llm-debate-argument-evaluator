import heapq
from typing import Any, Dict, List, Optional, Tuple

from config.priority_queue_config import priority_queue_config
from utils.logger import logger
from utils.state_saver import StateSaver


class PriorityQueueService:
    REMOVED = "<removed>"

    def __init__(self):
        self.queue = []
        self.entry_finder: Dict[str, Tuple[int, int, Dict[str, Any]]] = {}
        self.counter = 0
        self.state_saver = StateSaver()
        self.PRIORITY_LEVELS = priority_queue_config.PRIORITY_LEVELS
        logger.info("PriorityQueueService initialized")

    def add_node(self, node: Dict[str, Any], priority: str = "MEDIUM") -> None:
        """Add a new node or update existing node"""
        node_id = str(node["id"])
        if node_id in self.entry_finder:
            self.remove_node(node_id)

        # Convert priority string to numeric value
        priority_value = self._get_priority_value(priority)
        count = self.counter
        self.counter += 1

        entry = [-priority_value, count, node]  # Negative for max-heap behavior
        self.entry_finder[node_id] = entry
        heapq.heappush(self.queue, entry)
        logger.debug(f"Added/Updated node {node_id} with priority {priority}")

        # Save state after adding node
        self.state_saver.save_node_state(self.entry_finder, "node_add")

    def remove_node(self, node_id: str) -> None:
        """Mark an existing node as removed"""
        entry = self.entry_finder.pop(str(node_id))
        entry[2] = self.REMOVED

    def pop_node(self) -> Dict[str, Any]:
        """Remove and return the highest priority node"""
        while self.queue:
            priority, count, node = heapq.heappop(self.queue)
            if node is not self.REMOVED:
                node_id = str(node["id"])
                if node_id in self.entry_finder:
                    del self.entry_finder[node_id]
                    logger.debug(f"Popped node {node_id} with priority {-priority}")
                    return node
        raise KeyError("pop from an empty priority queue")

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node data from entry_finder"""
        entry = self.entry_finder.get(str(node_id))
        return entry[2] if entry else None

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all children of a node"""
        children = []
        for entry in self.entry_finder.values():
            node = entry[2]
            if node is not self.REMOVED and str(node.get("parent")) == str(parent_id):
                children.append(node)
        return children

    def get_all_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Get all nodes in the priority queue"""
        return {
            node_id: entry[2]
            for node_id, entry in self.entry_finder.items()
            if entry[2] is not self.REMOVED
        }

    def is_empty(self) -> bool:
        """Check if the priority queue is empty"""
        return len(self.entry_finder) == 0

    def get_unique_id(self) -> int:
        """Get a unique ID for new nodes"""
        unique_id = self.counter
        self.counter += 1
        return unique_id

    def _get_priority_value(self, priority: str) -> int:
        """Convert priority string to numeric value"""
        priority_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return priority_map.get(priority.upper(), 2)  # Default to MEDIUM

    def update_node(self, node_id, updated_node):
        """Update a node in the priority queue"""
        if node_id in self.entry_finder:
            self.entry_finder[node_id] = updated_node
        else:
            raise KeyError(f"Node with ID {node_id} not found in priority queue")
