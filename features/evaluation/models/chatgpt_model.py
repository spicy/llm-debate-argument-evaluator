"""
TODO: This module...
"""

from features.evaluation.api_clients.chatgpt_api_client import ChatGPTAPIClient
from utils.logger import logger

from .base_model import BaseLLMModel


class ChatGPTModel(BaseLLMModel):
    def __init__(self, api_client: ChatGPTAPIClient):
        """TODO: Add Simple Docstring"""
        super().__init__()
        logger.debug("Initializing ChatGPT model")
        self.api_client = api_client
        logger.info("ChatGPT model initialized successfully")

    async def evaluate(self, evaluation_type: str, argument: str) -> float:
        """TODO: Add Simple Docstring"""
        system_message = self.evaluation_messages[evaluation_type]
        prompt = f"Evaluate the following argument: '{argument}'"
        return await self.api_client.evaluate(system_message, prompt)

    async def generate(self, generation_type: str, prompt: str) -> str:
        """TODO: Add Simple Docstring"""
        system_message = self.generation_messages[generation_type]
        return await self.api_client.generate_text(system_message, prompt)
