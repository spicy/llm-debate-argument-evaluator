"""
TODO: This module...
"""

from typing import Dict

from config.score_aggregator_config import score_aggregator_config
from utils.logger import log_execution_time, logger


class ScoreAggregator:
    def __init__(self):
        """TODO: Add Simple Docstring"""
        self.weights = {
            "coherence": score_aggregator_config.COHERENCE_INFLUENCE,
            "persuasion": score_aggregator_config.PERSUASION_INFLUENCE,
            "factual_accuracy": score_aggregator_config.FACTUAL_ACCURACY_INFLUENCE,
            "cultural_acceptance": score_aggregator_config.CULTURAL_ACCEPTANCE_INFLUENCE,
        }
        logger.info(f"ScoreAggregator initialized with weights: {self.weights}")

    @log_execution_time
    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculates the weighted score based on predefined weights"""
        if not scores:
            return 0.0

        total_score = 0
        total_weight = 0

        for criterion, score in scores.items():
            weight = self.weights.get(criterion, 0)
            total_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        final_score = total_score / total_weight
        logger.debug(f"Calculated weighted score: {final_score}")
        return final_score
