"""
TODO: This module...
"""

from config.base_config import BaseConfig


class VectorDBConfig(BaseConfig):
    COLLECTION_NAME: str = "debate_arguments"


vector_db_config: VectorDBConfig = VectorDBConfig()
