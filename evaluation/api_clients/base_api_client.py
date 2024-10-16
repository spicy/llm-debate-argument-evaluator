from abc import ABC, abstractmethod

from config import api_config
from utils.logger import log_execution_time


class BaseAPIClient(ABC):
    @abstractmethod
    @log_execution_time
    async def evaluate(self, prompt: str) -> float:
        pass

    @abstractmethod
    def _get_headers(self):
        pass

    @abstractmethod
    def _prepare_request_data(self, prompt: str):
        pass

    @abstractmethod
    async def _check_response(self, response):
        pass

    @abstractmethod
    def _extract_score(self, result):
        pass
