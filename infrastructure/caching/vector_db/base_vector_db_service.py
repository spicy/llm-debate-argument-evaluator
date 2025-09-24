"""
TODO: This module...
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseVectorDBService(ABC):
    """Abstract base class for a vector database service."""

    @abstractmethod
    def add(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Adds or updates text embeddings in the vector database.
        """
        pass

    @abstractmethod
    def search(
        self, query_embedding: List[float], limit: int, threshold: float
    ) -> Optional[str]:
        """
        Searches for the most similar vector in the database.
        """
        pass
