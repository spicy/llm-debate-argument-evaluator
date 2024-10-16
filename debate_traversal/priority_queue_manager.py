import heapq
from typing import Any, Dict

from config import priority_queue_config
from utils.logger import logger


class PriorityQueueManager:
    def __init__(self):
        self.queue = []
        self.entry_finder: Dict[str, Any] = {}
        self.REMOVED = "<removed-task>"
        self.counter = 0
        logger.info("PriorityQueueManager initialized")

    def add_node(self, node_id: str, priority: str = "MEDIUM"):
        if priority not in priority_queue_config.PRIORITY_LEVELS:
            raise ValueError(
                f"Invalid priority level. Must be one of {list(priority_queue_config.PRIORITY_LEVELS.keys())}"
            )

        priority_value = priority_queue_config.PRIORITY_LEVELS[priority]
        if node_id in self.entry_finder:
            self.remove_node(node_id)

        entry = [priority_value, self.counter, node_id]
        self.entry_finder[node_id] = entry
        heapq.heappush(self.queue, entry)
        self.counter += 1
        logger.debug(f"Added node {node_id} with priority {priority}")

    def remove_node(self, node_id: str):
        entry = self.entry_finder.pop(node_id)
        entry[-1] = self.REMOVED
        logger.debug(f"Removed node {node_id}")

    def pop_node(self):
        while self.queue:
            priority, count, node_id = heapq.heappop(self.queue)
            if node_id is not self.REMOVED:
                del self.entry_finder[node_id]
                logger.debug(f"Popped node {node_id} with priority {priority}")
                return node_id
        raise KeyError("pop from an empty priority queue")

    def is_empty(self):
        return len(self.entry_finder) == 0
