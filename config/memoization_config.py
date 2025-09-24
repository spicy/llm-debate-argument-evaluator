"""
TODO: This module...
"""

from config.base_config import BaseConfig


class MemoizationConfig(BaseConfig):
    # Semantic similarity model
    SEMANTIC_SIMILARITY_MODEL: str = "all-MiniLM-L6-v2"

    # Cache file path
    CACHE_FILE_PATH: str = "data/argument_cache.json"

    # Similarity threshold for considering arguments as similar
    SIMILARITY_THRESHOLD: float = 0.95


memoization_config: MemoizationConfig = MemoizationConfig()
