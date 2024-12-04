from debate_traversal.traversal_logic import TraversalLogic
from utils.logger import logger


class TraversalInjector:
    @staticmethod
    def inject_traversal_services(dependency_registry):
        logger.info("Injecting traversal services")

        priority_queue_service = dependency_registry.get("priority_queue_service")
        traversal_logic = TraversalLogic(priority_queue_service)
        dependency_registry.register("traversal_logic", traversal_logic)

        logger.info("Traversal services injected successfully")
