from typing import Any, Dict

from commands.evaluate_arguments_command import EvaluateArgumentsCommand
from commands.expand_node_command import ExpandNodeCommand
from debate_traversal.traversal_logic import TraversalLogic
from services.priority_queue_service import PriorityQueueService
from utils.logger import log_execution_time, logger


class TraverseDebateCommand:
    def __init__(
        self,
        traversal_logic: TraversalLogic,
        priority_queue_service: PriorityQueueService,
        expand_node_command: ExpandNodeCommand,
        evaluate_arguments_command: EvaluateArgumentsCommand,
    ):
        self.traversal_logic = traversal_logic
        self.priority_queue_service = priority_queue_service
        self.expand_node_command = expand_node_command
        self.evaluate_arguments_command = evaluate_arguments_command

    @log_execution_time
    async def execute(self, topic: str, max_depth: int) -> None:
        try:
            logger.info(f"Starting debate traversal for topic: {topic}")

            # Generate root node
            root_node = {
                "id": self.priority_queue_service.get_unique_id(),
                "argument": topic,
                "category": "root",
                "topic": topic,
                "evaluation": 1.0,  # Root node gets highest priority
                "parent": -1,
                "depth": 0,
                "children": [],
            }

            self.priority_queue_service.add_node(root_node, "HIGH")
            root_node_id = str(root_node["id"])

            # Start traversal
            async for node in self.traversal_logic.traverse(
                root_node_id,
                self.priority_queue_service.get_node,
                self._expand_node,
                self._evaluate_node,
                max_depth,
            ):
                logger.debug(f"Traversed node: {node['id']}")

        except Exception as e:
            logger.error(f"Error during debate traversal: {str(e)}")
            raise

    async def _expand_node(self, node_id: str) -> list:
        """Expand a node and return its children"""
        await self.expand_node_command.execute(node_id)
        return self.priority_queue_service.get_children(node_id)

    async def _evaluate_node(self, node_id: str) -> Dict[str, float]:
        """Evaluate a node and return its scores"""
        node = self.priority_queue_service.get_node(node_id)
        if not node:
            return {}

        evaluation_results = await self.evaluate_arguments_command.execute(
            [node["argument"]]
        )
        return evaluation_results[0] if evaluation_results else {}
