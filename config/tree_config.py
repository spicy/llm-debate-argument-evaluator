"""
TODO: This module...
"""

from config.base_config import BaseConfig


class TreeConfig(BaseConfig):
    MAX_TREE_DEPTH: int = 5
    MAX_CHILDREN_PER_NODE: int = 3

    # Pruning configuration
    DEFAULT_PRUNE_THRESHOLD: float = -1.0  # -1.0 = always prompt user
    MIN_PRUNE_THRESHOLD: float = 0.1
    MAX_PRUNE_THRESHOLD: float = 0.95


tree_config: TreeConfig = TreeConfig()
