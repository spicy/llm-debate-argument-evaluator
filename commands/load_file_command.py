import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

from services.async_processing_service import AsyncProcessingService
from services.evaluation_service import EvaluationService
from services.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class LoadFileCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
        score_aggregator_service: ScoreAggregatorService,
        async_processing_service: AsyncProcessingService,
    ):
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service
        self.async_service = async_processing_service

    @log_execution_time
    async def execute(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r") as file:
                items = json.load(file)

            processed_nodes = []
            evaluation_tasks = []

            for item in items:
                # Create evaluation tasks
                evaluation_tasks.append(
                    self.async_service.process_async(
                        self.evaluation_service.evaluate_argument(item["argument"])
                    )
                )

            # Wait for all evaluations to complete
            evaluation_results = await asyncio.gather(*evaluation_tasks)

            # Process results and create nodes
            for item, result in zip(items, evaluation_results):
                try:
                    score = self.score_aggregator_service.average_scores(result)
                    new_node = {
                        "id": self.priority_queue_service.get_unique_id(),
                        "argument": item["argument"],
                        "category": item.get("category", "general"),
                        "topic": item.get("topic", "File Input"),
                        "subtopic": item.get(
                            "subcategory", item.get("category", "general")
                        ),
                        "evaluation": score,
                        "parent": item.get("parent", -1),
                    }

                    # Queue the new node for evaluation
                    await self.async_service.queue_evaluation(new_node)
                    processed_nodes.append(new_node)

                except Exception as e:
                    logger.error(f"Error processing argument: {str(e)}", exc_info=True)
                    continue

            return processed_nodes

        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            return []

    def _validate_argument(self, item: Dict[str, Any]) -> bool:
        """Validate the structure of an argument object"""
        if not isinstance(item, dict):
            logger.warning("Invalid item format - must be an object")
            return False

        if "argument" not in item:
            logger.warning("Missing required 'argument' field")
            return False

        if not isinstance(item["argument"], str):
            logger.warning("'argument' field must be a string")
            return False

        # Optional field validation
        optional_str_fields = ["category", "topic", "subcategory"]
        for field in optional_str_fields:
            if field in item and not isinstance(item[field], str):
                logger.warning(f"Optional field '{field}' must be a string if present")
                return False

        if "parent" in item and not isinstance(item["parent"], (int, str)):
            logger.warning(
                "Optional field 'parent' must be an integer or string if present"
            )
            return False

        return True
