from services.evaluation_service import EvaluationService
from services.interfaces.queue_service_interface import QueueServiceInterface
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class EvaluateDebateTreeCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        priority_queue_service: QueueServiceInterface,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self):
        """Evaluates all nodes in the debate tree"""
        logger.info("Starting debate tree evaluation")

        nodes = self.priority_queue_service.get_all_nodes()
        evaluation_results = {}

        for node_id, node in nodes.items():
            if node_id == "0":  # Skip root node
                continue
            evaluation_result = await self.evaluation_service.evaluate_argument(
                node["argument"]
            )
            score = self.score_aggregator_service.average_scores(evaluation_result)
            node["evaluation"] = score
            evaluation_results[node_id] = score

            # Update node in priority queue
            self.priority_queue_service.update_node(node_id, node)

        logger.info(f"Completed evaluation of {len(nodes)} nodes")
        return evaluation_results
