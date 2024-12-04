from typing import Dict, List

from utils.logger import log_execution_time, logger


class ScoreAggregator:
    @staticmethod
    @log_execution_time
    def aggregate_scores(
        evaluation_results: List[Dict[str, Dict[str, float]]]
    ) -> Dict[str, Dict[str, float]]:
        logger.debug("Starting score aggregation")
        aggregated_scores = {}
        for result in evaluation_results:
            for model, scores in result.items():
                if model not in aggregated_scores:
                    aggregated_scores[model] = scores
                else:
                    # Combine scores from same model
                    for criterion, score in scores.items():
                        if criterion not in aggregated_scores[model]:
                            aggregated_scores[model][criterion] = score
                        else:
                            aggregated_scores[model][criterion] = (
                                aggregated_scores[model][criterion] + score
                            ) / 2

        logger.debug("Score aggregation completed")
        return aggregated_scores

    def average_scores(self, evaluation_results: dict):
        # Add debug logging
        logger.debug(f"Raw evaluation results: {evaluation_results}")

        total_scores = {
            "coherence": 0.0,
            "persuasion": 0.0,
            "cultural_acceptance": 0.0,
            "factual_accuracy": 0.0,
        }
        for scores in evaluation_results.values():
            logger.debug(f"Processing model scores: {scores}")
            for criterion, score in scores.items():
                total_scores[criterion] += score

        # Log intermediate calculations
        logger.debug(f"Total scores before averaging: {total_scores}")
        for key in total_scores.keys():
            total_scores[key] /= len(evaluation_results)

        logger.debug(f"Final averaged scores: {total_scores}")
        final_score = sum(total_scores.values()) / len(total_scores)
        logger.debug(f"Final combined score: {final_score}")

        return final_score
