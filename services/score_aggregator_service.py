from utils.logger import log_execution_time, logger
from config import score_aggregator_config


class ScoreAggregatorService:
    @log_execution_time
    def aggregate_scores(self, evaluation_results: list):
        logger.debug("Aggregating scores")
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
            logger.debug(f"Aggregated scores for {model}: {final_scores[model]}")

        logger.debug("Score aggregation completed")
        return final_scores

    @log_execution_time
    def average_scores(self, evaluation_results: dict):
        logger.debug("Average scores")
        total_scores = {
            "coherence": 0.0,
            "persuasion": 0.0,
            "cultural_acceptance": 0.0,
            "factual_accuracy": 0.0,
        }

        for scores in evaluation_results.values():
            for criterion, score in scores.items():
                total_scores[criterion] += score

        for key in total_scores.keys():
            total_scores[key] /= 2

        logger.info(f"Average scores of both models: {total_scores}")
        
        # Influence of each critera has an influence on overall score (cultural acceptance 10%, factual 50%, coherence 20%, persuasion 20%)
        overall_score = 0.0

        overall_score += score_aggregator_config.COHERENCE_INFLUENCE * total_scores["coherence"]
        overall_score += score_aggregator_config.CULTURAL_ACCEPTANCE_INFLUENCE * total_scores["cultural_acceptance"]
        overall_score += score_aggregator_config.FACTUAL_ACCURACY_INFLUENCE * total_scores["factual_accuracy"]
        overall_score += score_aggregator_config.PERSUASION_INFLUENCE * total_scores["persuasion"]

        logger.info(f"Overall score of node {overall_score} completed")
        
        return overall_score
