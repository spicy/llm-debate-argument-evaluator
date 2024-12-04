from config.environment import environment_config, get_env_variable
from evaluation.api_clients.claude_api_client import ClaudeAPIClient
from utils.logger import log_execution_time, logger

from .base_model import BaseLLMModel


class ClaudeModel(BaseLLMModel):
    def __init__(self):
        super().__init__()
        logger.debug("Initializing Claude model")

        # Check if Claude is enabled
        if not environment_config.CLAUDE_ENABLED:
            logger.error("Attempting to initialize Claude model when it's not enabled")
            raise ValueError("Claude is not enabled in configuration")

        # Get API key
        self.api_key = get_env_variable("CLAUDE_API_KEY", None)
        if not self.api_key:
            logger.error("CLAUDE_API_KEY not found in environment variables")
            raise ValueError("CLAUDE_API_KEY is required for Claude model")

        # Get API endpoint
        self.api_endpoint = get_env_variable(
            "CLAUDE_API_ENDPOINT", "https://api.anthropic.com/v1/messages"
        )

        logger.info("Claude model initialized successfully")
        self.api_client = ClaudeAPIClient()

    @log_execution_time
    async def evaluate(self, evaluation_type: str, argument: str) -> float:
        system_message = self.evaluation_messages[evaluation_type]
        prompt = f"Evaluate the following argument: '{argument}'"
        return await self.api_client.evaluate(system_message, prompt)

    @log_execution_time
    async def generate(self, generation_type: str, prompt: str) -> str:
        system_message = self.generation_messages[generation_type]
        return await self.api_client.generate_text(system_message, prompt)
