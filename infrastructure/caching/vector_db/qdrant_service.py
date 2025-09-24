"""
TODO: This module...
"""

from typing import Any, Dict, List, Optional
import uuid

from qdrant_client import QdrantClient, models

from config import get_env_variable, vector_db_config
from infrastructure.caching.embedding_service import EmbeddingService
from infrastructure.caching.vector_db.base_vector_db_service import BaseVectorDBService
from utils.logger import logger


class QdrantService(BaseVectorDBService):
    """A service for interacting with a Qdrant vector database."""

    def __init__(self, embedding_service: EmbeddingService):
        """TODO: Add Simple Docstring"""
        url = get_env_variable("QDRANT_URL")
        api_key = get_env_variable("QDRANT_API_KEY")

        self.client = QdrantClient(url=url, api_key=api_key)
        self.embedding_service = embedding_service
        self.collection_name = vector_db_config.COLLECTION_NAME
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self) -> None:
        """Creates the Qdrant collection if it does not already exist."""
        try:
            self.client.get_collection(collection_name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists.")
        except Exception:
            logger.info(f"Collection '{self.collection_name}' not found. Creating...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_service.get_embedding_dimension(),
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(f"Collection '{self.collection_name}' created successfully.")

    def add(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Adds or updates points in the Qdrant collection.
        """
        if metadatas is None:
            metadatas = [{}] * len(texts)

        # Ensure text is included in the payload
        for i, meta in enumerate(metadatas):
            meta["text"] = texts[i]
            meta["cache_key"] = ids[i]

        # Convert string IDs to UUIDs
        try:
            uuid_ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, id_str)) for id_str in ids]
        except TypeError:
            # If ids are not strings, use them as is (e.g., if they are already UUIDs or integers)
            uuid_ids = ids

        self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=uuid_ids,
                vectors=embeddings,
                payloads=metadatas,
            ),
            wait=True,
        )
        logger.debug(
            f"Upserted {len(ids)} points to collection '{self.collection_name}'."
        )

    def search(
        self,
        query_embedding: List[float],
        limit: int = 1,
        threshold: Optional[float] = None,
    ) -> Optional[str]:
        """
        Searches for the most similar vector in the Qdrant collection.
        """
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=threshold,
        )

        if search_result:
            most_similar = search_result[0]
            logger.debug(
                f"Semantic search found a similar item with score: {most_similar.score}"
            )
            # The ID of a qdrant point can be an int or a string UUID.
            # Here we are using the cache key as the ID, which is a string.
            return most_similar.payload.get("cache_key")

        return None
