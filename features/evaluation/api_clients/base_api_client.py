"""
TODO: This module...
"""

from abc import ABC, abstractmethod

from config import api_config
from config.environment import environment_config
from utils.logger import log_execution_time


class BaseAPIClient(ABC):
    @abstractmethod
    @log_execution_time
    async def evaluate(
        self, system_message: str, prompt: str, max_tokens: int = 100
    ) -> float:
        pass

    @abstractmethod
    @log_execution_time
    async def generate_text(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int = environment_config.MAX_TOKENS,
    ) -> str:
        pass

    @abstractmethod
    def _get_headers(self):
        """TODO: Add Simple Docstring"""
        pass

    @abstractmethod
    def _prepare_request_data(self, prompt: str):
        """TODO: Add Simple Docstring"""
        pass

    @abstractmethod
    async def _check_response(self, response):
        """TODO: Add Simple Docstring"""
        pass

    @abstractmethod
    def _extract_score(self, result):
        """TODO: Add Simple Docstring"""
        pass
