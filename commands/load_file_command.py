import json
from pathlib import Path
from typing import Any, Dict, List

from services.evaluation_service import EvaluationService
from visualization.priority_queue_service import PriorityQueueService
from services.score_aggregator_service import ScoreAggregatorService
from utils.logger import log_execution_time, logger


class LoadFileCommand:
    def __init__(
        self,
        evaluation_service: EvaluationService,
        priority_queue_service: PriorityQueueService,
        score_aggregator_service: ScoreAggregatorService,
    ):
        self.evaluation_service = evaluation_service
        self.priority_queue_service = priority_queue_service
        self.score_aggregator_service = score_aggregator_service

    @log_execution_time
    async def execute(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load and process arguments from a JSON file.
        Returns a list of processed nodes for testing purposes.
        """
        logger.info(f"Loading arguments from file: {file_path}")
        processed_nodes = []

        try:
            # Validate and load file
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return processed_nodes

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.error("File must contain a JSON array of argument objects")
                return processed_nodes

            # Process each argument
            for item in data:
                try:
                    if not self._validate_argument(item):
                        logger.warning(f"Skipping invalid argument: {item}")
                        continue

                    # Log the full argument being processed
                    logger.debug(f"Processing argument: {item['argument']}")
                    evaluation_result = item.get("evaluation", None)
                    if evaluation_result is None:

                        # Evaluate the argument
                        evaluation_results = (
                            await self.evaluation_service.evaluate_argument(
                                item["argument"]
                            )
                        )

                        if not evaluation_results:
                            logger.error(
                                f"Failed to get evaluation results for argument: {item['argument'][:50]}..."
                            )
                            continue

                        evaluation_result = self.score_aggregator_service.average_scores(
                            evaluation_results
                        )
                        # evaluation_result = 0.5
                        logger.debug(
                            f"Evaluated argument: {item['argument']} with score {evaluation_result}"
                        )

                    # Create node with proper defaults
                    new_node = {
                        "id": self.priority_queue_service.get_unique_id(),
                        "argument": item["argument"],
                        "category": item.get("category", "general"),
                        "topic": item.get("topic", "File Input"),
                        "subtopic": item.get(
                            "subcategory", item.get("category", "general")
                        ),
                        "evaluation": evaluation_result,
                        "parent": item.get("parent", -1),
                        "depth": item.get("depth", 0),
                    }

                    # Add to priority queue and processed nodes
                    self.priority_queue_service.add_node(new_node)
                    processed_nodes.append(new_node)
                    logger.debug(f"Successfully processed argument: {new_node['id']}")

                except Exception as e:
                    logger.error(f"Error processing argument: {str(e)}", exc_info=True)
                    continue

            logger.info(
                f"Successfully loaded {len(processed_nodes)} arguments from file"
            )
            return processed_nodes

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in file {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}", exc_info=True)

        return processed_nodes

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
