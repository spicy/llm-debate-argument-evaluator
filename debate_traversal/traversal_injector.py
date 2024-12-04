from debate_traversal.priority_queue_manager import PriorityQueueManager
from debate_traversal.traversal_logic import TraversalLogic
from utils.logger import logger


class TraversalInjector:
    @staticmethod
    def inject_traversal_services(dependency_registry):
        logger.info("Injecting traversal services")

        priority_queue_manager = PriorityQueueManager()
        traversal_logic = TraversalLogic(priority_queue_manager)

        dependency_registry.register("priority_queue_manager", priority_queue_manager)
        dependency_registry.register("traversal_logic", traversal_logic)

        logger.info("Traversal services injected successfully")
