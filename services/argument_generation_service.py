import random
from typing import Dict, List

from config.environment import environment_config
from evaluation.api_clients.base_api_client import BaseAPIClient
from utils.async_utils import run_async_tasks
from utils.logger import log_execution_time, logger


class ArgumentGenerationService:
    def __init__(self, api_client: BaseAPIClient):
        self.api_client = api_client
        logger.info("ArgumentGenerationService initialized")

    @log_execution_time
    async def generate_arguments(
        self,
        topic: str,
        subcategory: str,
        support: str,
        against: str,
        num_arguments_per_side: int = 3,
    ) -> Dict[str, List[str]]:
        logger.info(
            f"Generating {num_arguments_per_side * 2} arguments for {topic} - {subcategory}"
        )

        async def generate_single_argument(prompt: str, stance: str) -> str:
            system_message = (
                f"You are an AI assistant tasked with generating a balanced and "
                f"well-reasoned argument {stance} the topic. Provide a concise argument "
                f"based on the given prompt, considering the {stance} perspective."
                f"The argument should be a single argument and to the point."
            )
            response = await self.api_client.generate_text(
                system_message=system_message, user_message=prompt
            )
            return response.strip()

        # Generate arguments asynchronously
        tasks_supporting = [
            generate_single_argument(support, "supporting")
            for _ in range(num_arguments_per_side)
        ]
        tasks_against = [
            generate_single_argument(against, "against")
            for _ in range(num_arguments_per_side)
        ]

        arguments_supporting = await run_async_tasks(tasks_supporting)
        arguments_against = await run_async_tasks(tasks_against)

        for i, argument in enumerate(arguments_supporting + arguments_against):
            stance = "supporting" if i < num_arguments_per_side else "against"
            logger.debug(
                f"Generated {stance} argument {i % num_arguments_per_side + 1}: {argument}"
            )

        logger.info(
            f"Generated {len(arguments_supporting)} supporting arguments and {len(arguments_against)} arguments against"
        )
        return arguments_supporting + arguments_against
