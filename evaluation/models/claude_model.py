from typing import Callable, Dict

from evaluation.api_clients.claude_api_client import ClaudeAPIClient
from utils.logger import log_execution_time, logger

from .base_model import BaseLLMModel


class ClaudeModel(BaseLLMModel):
    def __init__(self):
        self.api_client = ClaudeAPIClient()
        self.evaluation_prompts: Dict[str, Callable[[str], str]] = {
            "coherence": lambda arg: (
                f"Evaluate the coherence of the following argument on a decimal scale of 0 to 1.00: '{arg}'"
            ),
            "persuasion": lambda arg: (
                f"Evaluate the persuasiveness of the following argument on a scale of 0 to 100: '{arg}'"
            ),
            "cultural_acceptance": lambda arg: (
                f"Evaluate the cultural acceptance of the following argument on a scale of 0 to 100: '{arg}'"
            ),
            "factual_accuracy": lambda arg: (
                f"Evaluate the factual accuracy of the following argument giving on a scale of 0 to 100: '{arg}'"
            ),
        }

        self.eval_system_message = (
                f"You are an AI assistant tasked with evaluating the given argument in terms of the criteria given. "
                f"You must be an unbiased judge to the argument provided. "
                f"The evaluation should be only a value between 0 to 1. "
                f"Explicitly print out only the value as a float and nothing else. "
            )

    @log_execution_time
    async def _evaluate(self, evaluation_type: str, argument: str) -> float:
        if evaluation_type not in self.evaluation_prompts:
            logger.error(f"Invalid evaluation type: {evaluation_type}")
            raise ValueError(f"Invalid evaluation type: {evaluation_type}")
        prompt = self.evaluation_prompts[evaluation_type](argument)
        logger.debug(f"Evaluating {evaluation_type} for Claude model")
        return await self.api_client.evaluate(self.eval_system_message, prompt)
    
    @log_execution_time
    async def evaluate_coherence(self, argument: str) -> float:
        return await self._evaluate("coherence", argument)

    @log_execution_time
    async def evaluate_persuasion(self, argument: str) -> float:
        return await self._evaluate("persuasion", argument)

    @log_execution_time
    async def evaluate_cultural_acceptance(self, argument: str) -> float:
        return await self._evaluate("cultural_acceptance", argument)

    @log_execution_time
    async def evaluate_factual_accuracy(self, argument: str) -> float:
        return await self._evaluate("factual_accuracy", argument)
