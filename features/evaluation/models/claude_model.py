"""
TODO: This module...
"""

from config.environment import get_env_variable
from features.evaluation.api_clients.claude_api_client import ClaudeAPIClient
from utils.logger import log_execution_time, logger

from .base_model import BaseLLMModel


class ClaudeModel(BaseLLMModel):
    def __init__(self, api_client: ClaudeAPIClient):
        """TODO: Add Simple Docstring"""
        super().__init__()
        logger.info("Claude model initialized successfully")
        self.api_client = api_client

    @log_execution_time
    async def evaluate(self, evaluation_type: str, argument: str) -> float:
        """TODO: Add Simple Docstring"""
        system_message = self.evaluation_messages[evaluation_type]
        prompt = f"Evaluate the following argument: '{argument}'"
        return await self.api_client.evaluate(system_message, prompt)

    @log_execution_time
    async def generate(self, generation_type: str, prompt: str) -> str:
        """TODO: Add Simple Docstring"""
        system_message = self.generation_messages[generation_type]
        return await self.api_client.generate_text(system_message, prompt)
