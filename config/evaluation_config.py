"""
TODO: This module...
"""

from config.base_config import BaseConfig


class EvaluationConfig(BaseConfig):
    COHERENCE: str = "coherence"
    PERSUASION: str = "persuasion"
    CULTURAL_ACCEPTANCE: str = "cultural_acceptance"
    FACTUAL_ACCURACY: str = "factual_accuracy"


evaluation_config: EvaluationConfig = EvaluationConfig()
