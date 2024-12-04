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
                    aggregated_scores[model] = {k: [] for k in scores.keys()}
                for criterion, score in scores.items():
                    aggregated_scores[model][criterion].append(score)

        final_scores = {}
        for model, scores in aggregated_scores.items():
            final_scores[model] = {
                criterion: sum(score_list) / len(score_list)
                for criterion, score_list in scores.items()
            }

        logger.debug("Score aggregation completed")
        return final_scores
