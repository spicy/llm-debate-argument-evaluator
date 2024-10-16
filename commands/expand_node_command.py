from config import debate_tree_config  # MAX_CHILDREN_PER_NODE, MAX_TREE_DEPTH
from services.priority_queue_service import PriorityQueueService
from utils.logger import log_execution_time, logger
from visualization.node_expansion_handler import NodeExpansionHandler


class ExpandNodeCommand:
    def __init__(
        self,
        priority_queue_service: PriorityQueueService,
        node_expansion_handler: NodeExpansionHandler,
    ):
        self.priority_queue_service = priority_queue_service
        self.node_expansion_handler = node_expansion_handler

    @log_execution_time
    async def execute(self, node_id: str):
        logger.debug(f"Attempting to expand node with ID {node_id}")
        # Retrieve the node from the priority queue
        node = self.priority_queue_service.get_node(node_id)

        if not node:
            logger.warning(f"Node with ID {node_id} not found.")
            return

        # Expand the node in the debate tree
        expanded_nodes = await self.node_expansion_handler.expand_node(node)

        # Add expanded nodes to the priority queue
        for new_node in expanded_nodes:
            self.priority_queue_service.add_node(new_node)

        logger.info(
            f"Node {node_id} expanded successfully. Added {len(expanded_nodes)} new nodes."
        )
