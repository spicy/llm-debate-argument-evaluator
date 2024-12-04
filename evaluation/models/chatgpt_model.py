from config.environment import environment_config, get_env_variable
from evaluation.api_clients.chatgpt_api_client import ChatGPTAPIClient
from utils.logger import log_execution_time, logger

from .base_model import BaseLLMModel


class ChatGPTModel(BaseLLMModel):
    def __init__(self):
        super().__init__()
        logger.debug("Initializing ChatGPT model")

        # Check if ChatGPT is enabled
        if not environment_config.CHATGPT_ENABLED:
            logger.error("Attempting to initialize ChatGPT model when it's not enabled")
            raise ValueError("ChatGPT is not enabled in configuration")

        # Get API key
        self.api_key = get_env_variable("CHATGPT_API_KEY", None)
        if not self.api_key:
            logger.error("CHATGPT_API_KEY not found in environment variables")
            raise ValueError("CHATGPT_API_KEY is required for ChatGPT model")

        # Get API endpoint
        self.api_endpoint = get_env_variable(
            "CHATGPT_API_ENDPOINT", "https://api.openai.com/v1/chat/completions"
        )

        logger.info("ChatGPT model initialized successfully")
        self.api_client = ChatGPTAPIClient()

    async def evaluate(self, evaluation_type: str, argument: str) -> float:
        system_message = self.evaluation_messages[evaluation_type]
        prompt = f"Evaluate the following argument: '{argument}'"
        return await self.api_client.evaluate(system_message, prompt)

    async def generate(self, generation_type: str, prompt: str) -> str:
        system_message = self.generation_messages[generation_type]
        return await self.api_client.generate_text(system_message, prompt)
