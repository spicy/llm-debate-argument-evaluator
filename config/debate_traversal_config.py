class DebateTraversalConfig:
    # Maximum depth for the debate tree
    MAX_TREE_DEPTH = 10

    # Maximum number of children per node
    MAX_CHILDREN_PER_NODE = 5

    # Priority levels for the queue
    PRIORITY_LEVELS = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    # Threshold for considering an argument as high priority
    HIGH_PRIORITY_THRESHOLD = 0.6

    # Threshold for considering an argument as low priority
    LOW_PRIORITY_THRESHOLD = 0.3


debate_traversal_config = DebateTraversalConfig()
