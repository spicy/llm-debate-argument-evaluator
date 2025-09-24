"""
TODO: This module...
"""

from typing import List

from sentence_transformers import SentenceTransformer

from config import memoization_config
from utils.logger import log_execution_time, logger


class EmbeddingService:
    """A service for generating sentence embeddings."""

    def __init__(self, model_name: str = memoization_config.SEMANTIC_SIMILARITY_MODEL):
        """TODO: Add Simple Docstring"""
        self.model = SentenceTransformer(model_name)
        logger.info(f"EmbeddingService initialized with model: {model_name}")

    def get_embedding_dimension(self) -> int:
        """Returns the dimension of the embeddings produced by the model."""
        dimension = self.model.get_sentence_embedding_dimension()
        if dimension is None:
            # Handle cases where the dimension isn't directly available
            sample_embedding = self.get_embedding("test")
            return len(sample_embedding)
        return dimension

    @log_execution_time
    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for a given text.
        """
        logger.debug(f"Generating embedding for text: '{text[:50]}...'")
        embedding = self.model.encode(text, convert_to_tensor=False).tolist()
        logger.debug("Embedding generated successfully.")
        return embedding
