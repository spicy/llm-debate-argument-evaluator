class MemoizationConfig:
    # Semantic similarity model
    SEMANTIC_SIMILARITY_MODEL = "all-MiniLM-L6-v2"

    # Cache file path
    CACHE_FILE_PATH = "data/argument_cache.json"

    # Similarity threshold for considering arguments as similar
    SIMILARITY_THRESHOLD = 0.95


memoization_config = MemoizationConfig()
