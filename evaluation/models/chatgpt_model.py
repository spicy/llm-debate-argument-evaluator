from typing import Callable, Dict

from evaluation.api_clients.chatgpt_api_client import ChatGPTAPIClient
from utils.logger import log_execution_time, logger

from .base_model import BaseLLMModel


class ChatGPTModel(BaseLLMModel):
    def __init__(self):
        self.api_client = ChatGPTAPIClient()
        self.evaluation_prompts: Dict[str, Callable[[str], str]] = {
            "coherence": lambda arg: (
                f"Evaluate the coherence of the following argument on a scale of 0 to 100: '{arg}'"
            ),
            "persuasion": lambda arg: (
                f"Evaluate the persuasiveness of the following argument on a scale of 0 to 100: '{arg}'"
            ),
            "cultural_acceptance": lambda arg: (
                f"Evaluate the cultural acceptance of the following argument on a scale of 0 to 100: '{arg}'"
            ),
            "factual_accuracy": lambda arg: (
                f"Evaluate the factual accuracy of the following argument on a scale of 0 to 100: '{arg}'"
            ),
        }

    @log_execution_time
    async def _evaluate(self, evaluation_type: str, argument: str) -> float:
        if evaluation_type not in self.evaluation_prompts:
            logger.error(f"Invalid evaluation type: {evaluation_type}")
            raise ValueError(f"Invalid evaluation type: {evaluation_type}")
        prompt = self.evaluation_prompts[evaluation_type](argument)
        logger.debug(f"Evaluating {evaluation_type} for ChatGPT model")
        return await self.api_client.evaluate(prompt)

    async def evaluate_coherence(self, argument: str) -> float:
        return await self._evaluate("coherence", argument)

    async def evaluate_persuasion(self, argument: str) -> float:
        return await self._evaluate("persuasion", argument)

    async def evaluate_cultural_acceptance(self, argument: str) -> float:
        return await self._evaluate("cultural_acceptance", argument)

    async def evaluate_factual_accuracy(self, argument: str) -> float:
        return await self._evaluate("factual_accuracy", argument)
