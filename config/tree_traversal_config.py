"""
TODO: This module...
"""

from typing import Dict

from config.base_config import BaseConfig


class TreeTraversalConfig(BaseConfig):
    # Maximum depth for the tree
    MAX_TREE_DEPTH: int = 10

    # Maximum number of children per node
    MAX_CHILDREN_PER_NODE: int = 5

    # Priority levels for the queue
    PRIORITY_LEVELS: Dict[str, int] = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    # Threshold for considering an argument as high priority
    HIGH_PRIORITY_THRESHOLD: float = 0.6

    # Threshold for considering an argument as low priority
    LOW_PRIORITY_THRESHOLD: float = 0.3


tree_traversal_config: TreeTraversalConfig = TreeTraversalConfig()
