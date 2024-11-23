import heapq

from config import priority_queue_config
from utils.logger import logger


class PriorityQueueService:
    def __init__(self):
        self.queue = []
        self.entry_finder = {}
        self.REMOVED = "<removed-task>"
        self.counter = 0
        logger.info("PriorityQueueService initialized")

    def add_node(self, node, priority="MEDIUM"):
        if priority not in priority_queue_config.PRIORITY_LEVELS:
            raise ValueError(
                f"Invalid priority level. Must be one of {list(priority_queue_config.PRIORITY_LEVELS.keys())}"
            )
        priority_value = priority_queue_config.PRIORITY_LEVELS[priority]
        if node["id"] in self.entry_finder:
            self.remove_node(node["id"])
        entry = [priority_value, self.counter, node]
        self.entry_finder[node["id"]] = entry
        heapq.heappush(self.queue, entry)
        self.counter += 1
        logger.debug(f"Added node {node['id']} with priority {priority}")

    def remove_node(self, node_id):
        entry = self.entry_finder.pop(node_id)
        entry[-1] = self.REMOVED
        logger.debug(f"Removed node {node_id}")

    def get_node(self, node_id):
        node = (
            self.entry_finder.get(node_id)[-1] if node_id in self.entry_finder else None
        )
        logger.debug(f"Retrieved node {node_id}: {'Found' if node else 'Not found'}")
        return node

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
