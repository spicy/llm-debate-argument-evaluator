"""
TODO: This module...
"""

from config.base_config import BaseConfig


class ApiConfig(BaseConfig):
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2  # seconds


api_config: ApiConfig = ApiConfig()
