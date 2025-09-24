"""
TODO: This module...
"""

from features.evaluation.api_clients.google_api_client import GoogleAPIClient
from utils.logger import logger

from .base_model import BaseLLMModel


class GoogleModel(BaseLLMModel):
    def __init__(self, api_client: GoogleAPIClient):
        """TODO: Add Simple Docstring"""
        super().__init__()
        logger.debug("Initializing Google Gemini model")
        self.api_client = api_client
        logger.info("Google Gemini model initialized successfully")

    async def evaluate(self, evaluation_type: str, argument: str) -> float:
        """TODO: Add Simple Docstring"""
        system_message = self.evaluation_messages[evaluation_type]
        prompt = f"Evaluate the following argument: '{argument}'"
        return await self.api_client.evaluate(system_message, prompt)

    async def generate(self, generation_type: str, prompt: str) -> str:
        """TODO: Add Simple Docstring"""
        system_message = self.generation_messages[generation_type]
        return await self.api_client.generate_text(system_message, prompt)
