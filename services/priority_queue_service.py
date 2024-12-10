import heapq
from typing import Any, Dict, List, Optional

from config.debate_traversal_config import debate_traversal_config
from config.priority_queue_config import priority_queue_config
from services.interfaces.queue_service_interface import QueueServiceInterface
from utils.logger import logger
from utils.state_saver import StateSaver
from visualization.observer import Subject


class PriorityQueueService(Subject, QueueServiceInterface):
    REMOVED = "<removed>"

    def __init__(self):
        super().__init__()
        self._debate_tree = {}
        self.queue = []  # Maintain a heap queue for efficient priority handling
        self.entry_finder = (
            {}
        )  # Store node data and priority for quick lookup separate from the queue
        self.counter = 0
        self.state_saver = StateSaver()
        self.PRIORITY_LEVELS = priority_queue_config.PRIORITY_LEVELS
        logger.info("PriorityQueueService initialized")

    @property
    def debate_tree(self) -> Dict[str, Any]:
        return self._debate_tree

    def add_node(self, node: Dict[str, Any], priority: str = "MEDIUM") -> None:
        """Add a new node or update existing node"""
        if not isinstance(node, dict):
            logger.error(f"Invalid node format: {node}")
            return

        node_id = str(node["id"])
        parent_id = str(node.get("parent", -1))

        # Special handling for root node or nodes with no parent
        if parent_id == "-1":
            self._add_node_to_tree(node, priority)
            return

        # Check if parent exists before adding child
        if parent_id not in self._debate_tree:
            logger.error(
                f"Cannot add node {node_id}: Parent {parent_id} does not exist"
            )
            return

        self._add_node_to_tree(node, priority)

    def _add_node_to_tree(self, node: Dict[str, Any], priority: str) -> None:
        """Helper method to add node to both tree and queue"""
        node_id = str(node["id"])

        # Update debate tree first
        self._debate_tree[node_id] = node.copy()

        # Update priority queue
        if node_id in self.entry_finder:
            self.remove_node(node_id)

        priority_value = self._get_priority_value(priority)
        count = self.counter
        self.counter += 1

        entry = (
            -priority_value,
            count,
            int(node_id),
            node.copy(),
        )

        heapq.heappush(self.queue, entry)
        self.entry_finder[node_id] = entry

        # Save state and notify observers
        self.state_saver.save_node_state(self.entry_finder, "node_add")
        logger.debug(f"Added/Updated node {node_id} with priority {priority}")
        self.notify()

    def remove_node(self, node_id: str) -> None:
        """Mark an existing node as removed from queue but keep in debate tree"""
        node_id = str(node_id)
        entry = self.entry_finder.pop(node_id, None)
        if entry:
            # Only mark as removed in queue, don't remove from debate tree
            self.entry_finder[node_id] = (
                entry[0],  # priority
                entry[1],  # count
                entry[2],  # node_id
                self.REMOVED,  # mark as removed
            )
            logger.debug(f"Marked node {node_id} as removed from queue")
            self.notify()

    def pop_node(self) -> Dict[str, Any]:
        """Remove and return the highest priority node"""
        while self.queue:
            priority, count, node_id, node = heapq.heappop(self.queue)
            if node is not self.REMOVED:
                # Don't remove from debate tree, just return a copy
                logger.debug(f"Popped node {node_id} with priority {-priority}")
                return node.copy()
        raise KeyError("pop from an empty priority queue")

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node data from entry_finder"""
        entry = self.entry_finder.get(str(node_id))
        if not entry or not isinstance(entry, tuple) or len(entry) < 4:
            logger.warning(f"Node {node_id} not found or invalid entry format")
            return None

        node = entry[3]  # Node data is at index 3
        if node is self.REMOVED:
            return None
        return node.copy() if isinstance(node, dict) else None

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all children of a node"""
        children = []
        for entry in self.entry_finder.values():
            if not isinstance(entry, tuple) or len(entry) < 4:
                continue
            node = entry[3]  # Node data is at index 3
            if isinstance(node, dict) and node is not self.REMOVED:
                if str(node.get("parent")) == str(parent_id):
                    children.append(node.copy())
        return children

    def get_all_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Get all nodes in the priority queue"""
        return {
            node_id: entry[3].copy()  # Node data is at index 3
            for node_id, entry in self.entry_finder.items()
            if entry[3] is not self.REMOVED
        }

    def is_empty(self) -> bool:
        """Check if the priority queue is empty"""
        # Clean up any REMOVED entries from the queue
        while (
            self.queue and self.queue[0][3] is self.REMOVED
        ):  # Check index 3 for node data
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
            and isinstance(existing_entry, tuple)
            and len(existing_entry) >= 4
        ):
            # Update debate tree first
            self._debate_tree[node_id] = node.copy()

            priority_value = -existing_entry[0]
            priority = self._get_priority_from_int_to_str(priority_value)
            self.remove_node(node_id)
            self.add_node(node.copy(), priority)
            logger.debug(f"Updated node {node_id} with preserved priority {priority}")
        else:
            logger.warning(f"Attempted to update non-existent node {node_id}")
            score = node.get("evaluation", 0.5)
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
            and isinstance(entry, tuple)
            and len(entry) >= 4
            and entry[3] is not self.REMOVED
        )

    def notify(self):
        logger.debug(
            f"Tree state changed. Current nodes: {list(self._debate_tree.keys())}"
        )
        super().notify()
