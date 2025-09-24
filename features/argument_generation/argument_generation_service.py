"""
TODO: This module...
"""

from typing import Dict, List

from config.environment import environment_config
from features.evaluation.models.base_model import BaseLLMModel
from utils.async_utils import run_async_tasks
from utils.logger import log_execution_time, logger
from features.argument_generation.prompt_factory import PromptFactory


class ArgumentGenerationService:
    def __init__(self, api_client: BaseLLMModel):
        """TODO: Add Simple Docstring"""
        self.api_client = api_client
        logger.info(
            f"ArgumentGenerationService initialized with {api_client.__class__.__name__}"
        )

    @log_execution_time
    async def generate_arguments(
        self,
        topic: str,
        subcategory: str,
        argument_text: str,
        num_arguments: int,
    ) -> List[Dict]:
        """TODO: Add Simple Docstring"""
        try:
            half_num_arguments = num_arguments // 2

            support_prompt = PromptFactory.create_support_prompt(
                argument_text, topic, subcategory
            )
            against_prompt = PromptFactory.create_against_prompt(
                argument_text, topic, subcategory
            )

            tasks_supporting = [
                self.api_client.generate("supporting", support_prompt)
                for _ in range(half_num_arguments)
            ]
            tasks_against = [
                self.api_client.generate("against", against_prompt)
                for _ in range(half_num_arguments)
            ]

            arguments_supporting = await run_async_tasks(tasks_supporting)
            arguments_against = await run_async_tasks(tasks_against)

            # Convert to list of dicts with argument type
            result = []
            for arg in arguments_supporting:
                if arg:
                    result.append({"text": arg, "type": "supporting"})
            for arg in arguments_against:
                if arg:
                    result.append({"text": arg, "type": "against"})

            return result
        except Exception as e:
            logger.error(
                f"Error generating arguments for '{argument_text[:30]}...': {e}",
                exc_info=True,
            )
            return []
