from typing import Dict, Optional

from commands.generate_debate_arguments_command import GenerateDebateArgumentsCommand
from config import debate_traversal_config, debate_tree_config
from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class ExpandNodeCommand:
    def __init__(
        self,
        generate_debate_arguments_command: GenerateDebateArgumentsCommand,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.generate_debate_arguments_command = generate_debate_arguments_command
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self, node_id: str):
        """Expands a node by generating and adding child arguments"""
        logger.debug(f"Attempting to expand node with ID {node_id}")

        # Validate node exists
        if not self.priority_queue_service.node_exists(str(node_id)):
            logger.error(f"Cannot expand non-existent node: {node_id}")
            return []

        node = self.priority_queue_service.get_node(str(node_id))
        existing_children = self.priority_queue_service.get_children(str(node_id))

        if len(existing_children) >= debate_tree_config.MAX_CHILDREN_PER_NODE:
            logger.warning(f"Node {node_id} already has maximum children")
            return existing_children

        try:
            arguments = await self.generate_debate_arguments_command.execute(
                node["argument"], node.get("category", "general")
            )

            new_nodes = []
            for argument in arguments:
                new_node = await self._create_child_node(node, argument)
                if new_node:
                    new_nodes.append(new_node)

            return new_nodes

        except Exception as e:
            logger.error(f"Error expanding node {node_id}: {str(e)}")
            return []

    async def _create_child_node(
        self, parent_node: Dict, argument: str
    ) -> Optional[Dict]:
        """Helper method to create and evaluate a child node"""
        try:
            evaluation_result = await self.evaluation_service.evaluate_argument(
                argument
            )
            score = self.score_aggregator_service.average_scores(evaluation_result)

            new_node = {
                "id": self.priority_queue_service.get_unique_id(),
                "argument": argument,
                "category": parent_node["category"],
                "topic": parent_node.get("topic", "Unknown"),
                "subtopic": parent_node.get("subtopic", parent_node["category"]),
                "evaluation": score,
                "parent": parent_node["id"],
                "depth": parent_node.get("depth", 0) + 1,
            }

            priority = self._determine_priority(score)
            self.priority_queue_service.add_node(new_node, priority)
            return new_node

        except Exception as e:
            logger.error(f"Error creating child node: {str(e)}")
            return None

    def _determine_priority(self, score: float) -> str:
        """Helper method to determine priority based on score"""
        priority = "MEDIUM"  # Default priority
        if score >= debate_traversal_config.HIGH_PRIORITY_THRESHOLD:
            priority = "HIGH"
        elif score <= debate_traversal_config.LOW_PRIORITY_THRESHOLD:
            priority = "LOW"
        return priority
