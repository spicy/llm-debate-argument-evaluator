"""
TODO: This module...
"""

from features.evaluation.score_aggregator import ScoreAggregator
from utils.logger import log_execution_time, logger


class ScoreAggregatorService:
    def __init__(self, score_aggregator: ScoreAggregator):
        """TODO: Add Simple Docstring"""
        self.score_aggregator = score_aggregator
        logger.info("ScoreAggregatorService initialized")

    @log_execution_time
    def aggregate_scores(self, evaluation_results: dict) -> dict:
        logger.debug(f"Raw evaluation results: {evaluation_results}")
        if not evaluation_results:
            return {"details": {}, "average": 0.0}

        total_scores = {
            "coherence": 0.0,
            "persuasion": 0.0,
            "cultural_acceptance": 0.0,
            "factual_accuracy": 0.0,
        }
        num_models = len(evaluation_results)
        if num_models == 0:
            return {"details": {}, "average": 0.0}

        for model, scores in evaluation_results.items():
            logger.debug(f"Processing model scores for {model}: {scores}")
            for criterion, score in scores.items():
                if criterion in total_scores:
                    if isinstance(score, (int, float)):
                        total_scores[criterion] += score
                    else:
                        logger.warning(
                            f"Invalid score type for {criterion} from {model}: {type(score)}. Skipping."
                        )

        # Log intermediate calculations
        logger.debug(f"Total scores before averaging: {total_scores}")
        averaged_scores = {
            key: value / num_models for key, value in total_scores.items()
        }

        logger.debug(f"Final averaged scores: {averaged_scores}")
        final_score = self.score_aggregator.calculate_weighted_score(averaged_scores)
        logger.debug(f"Final combined score: {final_score}")

        return {"details": averaged_scores, "average": final_score}
