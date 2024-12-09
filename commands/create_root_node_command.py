from visualization.priority_queue_service import PriorityQueueService
from utils.logger import log_execution_time, logger


class CreateRootNodeCommand:
    def __init__(self, priority_queue_service: PriorityQueueService):
        self.priority_queue_service = priority_queue_service

    @log_execution_time
    async def execute(self, topic: str) -> str:
        """Creates a root node for the debate tree with the given topic"""
        logger.info(f"Creating root node for topic: {topic}")

        root_node = {
            "id": self.priority_queue_service.get_unique_id(),
            "argument": topic,
            "category": "root",
            "topic": topic,
            "evaluation": 0.1,  # Root node should get a neutral evaluation (logic .5 * .5 = .25) (accpetance .5 * .1 = .05) (coherence .5 * .2 = .1) (persuasion .5 * .2 = .1) (total = .5)
            "parent": -1,
            "depth": 0,
            "children": [],
        }

        self.priority_queue_service.add_node(root_node, "HIGH")
        root_node_id = str(root_node["id"])

        logger.info(f"Created root node with ID: {root_node_id}")
        return root_node_id
