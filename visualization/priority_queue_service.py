import heapq
from typing import Any, Dict, List, Optional, Tuple

from config.debate_traversal_config import debate_traversal_config
from config.priority_queue_config import priority_queue_config
from utils.logger import logger
from utils.state_saver import StateSaver
from visualization.observer import DebateTreeSubject


class PriorityQueueService(DebateTreeSubject):
    REMOVED = "<removed>"

    def __init__(self):
        super().__init__()
        self.queue = []  # Maintain a heap queue for efficient priority handling
        self.entry_finder = (
            {}
        )  # Store node data and priority for quick lookup separate from the queue
        self.counter = 0
        self.state_saver = StateSaver()
        self.PRIORITY_LEVELS = priority_queue_config.PRIORITY_LEVELS
        logger.info("PriorityQueueService initialized")

    def add_node(self, node: Dict[str, Any], priority: str = "MEDIUM") -> None:
        """Add a new node or update existing node"""
        if not isinstance(node, dict):
            logger.error(f"Invalid node format: {node}")
            return

        node_id = str(node["id"])
        parent_id = str(node.get("parent", -1))

        # Ensure parent exists in tree before adding child
        if parent_id != "-1" and parent_id not in self._debate_tree:
            logger.warning(
                f"Attempting to add node {node_id} with non-existent parent {parent_id}"
            )
            return
        self._debate_tree[node_id] = node.copy()

        if node_id in self.entry_finder:
            self.remove_node(node_id)

        # Convert priority string to numeric value
        priority_value = self._get_priority_value(priority)

        # Store the complete node object
        entry = [
            -priority_value,
            int(node_id),
            node.copy(),
        ]  # Make a copy to prevent reference issues

        heapq.heappush(self.queue, entry)
        self.entry_finder[node_id] = (
            entry.copy()
        )  # Issue here was becasue the entry changes one to <removed> after the first pop, but changes queue[0] to <removed> in queue

        # Save state after adding node
        self.state_saver.save_node_state(self.entry_finder, "node_add")
        logger.debug(f"Added/Updated node {node_id} with priority {priority}")

        # Notify observers of the change
        self.notify()

    def remove_node(self, node_id: str) -> None:
        """Mark an existing node as removed"""
        entry = self.entry_finder.pop(str(node_id))
        if entry:
            entry[2] = self.REMOVED
        logger.debug(f"Removed node {node_id}")

    def pop_node(self) -> Dict[str, Any]:
        """Remove and return the highest priority node"""
        while self.queue:
            priority, count, node = heapq.heappop(self.queue)
            if node is not self.REMOVED:
                node_id = str(node["id"])
                # Don't remove from entry_finder to preserve node data
                logger.debug(f"Popped node {node_id} with priority {-priority}")
                return node.copy()  # Return a copy to prevent modifications
        raise KeyError("pop from an empty priority queue")

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node data from entry_finder"""
        entry = self.entry_finder.get(str(node_id))
        if not entry or not isinstance(entry, (list, tuple)) or len(entry) < 3:
            logger.warning(f"Node {node_id} not found or invalid entry format")
            return None

        node = entry[2]
        if node is self.REMOVED:
            return None

        # Return a copy of the node to prevent accidental modifications
        return node.copy() if isinstance(node, dict) else None

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all children of a node"""
        children = []
        for entry in self.entry_finder.values():
            if not isinstance(entry, (list, tuple)) or len(entry) < 3:
                continue
            node = entry[2]
            if isinstance(node, dict) and node is not self.REMOVED:
                if str(node.get("parent")) == str(parent_id):
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
        # Clean up any REMOVED entries from the queue
        while self.queue and self.queue[0][2] is self.REMOVED:
            heapq.heappop(self.queue)
        return len(self.queue) == 0

    def get_unique_id(self) -> int:
        """Get a unique ID for new nodes"""
        unique_id = self.counter
        self.counter += 1
        return unique_id

    def _get_priority_value(self, priority: Any) -> int:
        """Convert priority string or number to numeric value"""
        if isinstance(priority, (int, float)):
            return int(priority)

        priority_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        if isinstance(priority, str):
            return priority_map.get(priority.upper(), 2)  # Default to MEDIUM
        return 2  # Default to MEDIUM for unknown types

    def update_node(self, node_id: str, node: Dict[str, Any]) -> None:
        """Update an existing node while preserving its priority"""
        if not isinstance(node, dict):
            logger.error(f"Invalid node data format for update: {node}")
            return

        node_id = str(node_id)
        existing_entry = self.entry_finder.get(node_id)

        if (
            existing_entry
            and isinstance(existing_entry, (list, tuple))
            and len(existing_entry) >= 3
        ):

            priority_value = -existing_entry[0]  # Get original priority
            priority = self._get_priority_from_int_to_str(priority_value)  # int to str
            self.remove_node(node_id)  # Remove from entry finder
            self.add_node(node.copy(), priority)  # Make a copy of the node
            logger.debug(f"Updated node {node_id} with preserved priority {priority}")
        else:
            logger.warning(f"Attempted to update non-existent node {node_id}")
            # Use evaluation score as priority if available, otherwise default to MEDIUM
            score = node.get("evaluation", 0.5)  # Default is 0.5 (MEDIUM)
            priority = self._get_priority_from_score(score)
            self.add_node(node.copy(), priority)

    def _get_priority_from_int_to_str(self, priority: int) -> str:
        """Convert priority value to string"""
        if priority == 3:
            return "HIGH"
        if priority == 1:
            return "LOW"
        return "MEDIUM"

    def _get_priority_from_score(self, node_score: float) -> str:
        """Get priority level based on node score"""
        if node_score >= debate_traversal_config.HIGH_PRIORITY_THRESHOLD:
            return "HIGH"
        if node_score <= debate_traversal_config.LOW_PRIORITY_THRESHOLD:
            return "LOW"
        return "MEDIUM"

    def node_exists(self, node_id: str) -> bool:
        """Check if a node exists and is not marked as removed"""
        entry = self.entry_finder.get(str(node_id))
        return (
            entry is not None
            and isinstance(entry, (list, tuple))
            and len(entry) >= 3
            and entry[2] is not self.REMOVED
        )

    def notify(self):
        logger.debug(
            f"Tree state changed. Current nodes: {list(self._debate_tree.keys())}"
        )
        super().notify()
