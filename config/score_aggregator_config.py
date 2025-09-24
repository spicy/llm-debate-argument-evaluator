"""
TODO: This module...
"""

from config.base_config import BaseConfig


class ScoreAggregatorConfig(BaseConfig):
    CULTURAL_ACCEPTANCE_INFLUENCE: float = 0.10
    FACTUAL_ACCURACY_INFLUENCE: float = 0.50
    COHERENCE_INFLUENCE: float = 0.20
    PERSUASION_INFLUENCE: float = 0.20


score_aggregator_config: ScoreAggregatorConfig = ScoreAggregatorConfig()
