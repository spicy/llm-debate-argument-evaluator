from typing import List

from config.environment import environment_config
from evaluation.api_clients.base_api_client import BaseAPIClient
from evaluation.models.base_model import BaseLLMModel
from utils.async_utils import run_async_tasks
from utils.logger import log_execution_time, logger


class ArgumentGenerationService:
    def __init__(self, api_client: BaseLLMModel):
        self.api_client = api_client
        logger.info(
            f"ArgumentGenerationService initialized with {api_client.__class__.__name__}"
        )

    @log_execution_time
    async def generate_arguments(
        self,
        topic: str,
        subcategory: str,
        support_prompt: str,
        against_prompt: str,
        num_arguments_per_side: int = 3,
    ) -> List[str]:
        tasks_supporting = [
            self.api_client.generate("supporting", support_prompt)
            for _ in range(num_arguments_per_side)
        ]
        tasks_against = [
            self.api_client.generate("against", against_prompt)
            for _ in range(num_arguments_per_side)
        ]

        arguments_supporting = await run_async_tasks(tasks_supporting)
        arguments_against = await run_async_tasks(tasks_against)

        return arguments_supporting + arguments_against
