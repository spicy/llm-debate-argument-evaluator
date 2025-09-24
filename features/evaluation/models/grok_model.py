"""
TODO: This module...
"""

from config.environment import get_env_variable
from features.evaluation.api_clients.grok_api_client import GrokAPIClient
from utils.logger import log_execution_time, logger

from .base_model import BaseLLMModel


class GrokModel(BaseLLMModel):
    def __init__(self, api_client: GrokAPIClient):
        """TODO: Add Simple Docstring"""
        super().__init__()
        logger.info("Grok model initialized successfully")
        self.api_client = api_client

    async def evaluate(self, evaluation_type: str, argument: str) -> float:
        """TODO: Add Simple Docstring"""
        system_message = self.evaluation_messages[evaluation_type]
        prompt = f"Evaluate the following argument: '{argument}'"
        return await self.api_client.evaluate(system_message, prompt)

    async def generate(self, generation_type: str, prompt: str) -> str:
        """TODO: Add Simple Docstring"""
        system_message = self.generation_messages[generation_type]
        return await self.api_client.generate_text(system_message, prompt)
