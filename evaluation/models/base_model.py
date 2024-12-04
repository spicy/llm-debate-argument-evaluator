from abc import ABC, abstractmethod

from config.system_messages_config import system_messages_config
from utils.logger import log_execution_time


class BaseLLMModel(ABC):
    def __init__(self):
        self.evaluation_messages = system_messages_config.EVALUATION_MESSAGES
        self.generation_messages = system_messages_config.GENERATION_MESSAGES

    @abstractmethod
    async def evaluate(self, evaluation_type: str, argument: str) -> float:
        """Base evaluation method"""
        pass

    @abstractmethod
    async def generate(self, generation_type: str, prompt: str) -> str:
        """Base generation method"""
        pass

    async def evaluate_coherence(self, argument: str) -> float:
        return await self.evaluate("coherence", argument)

    async def evaluate_persuasion(self, argument: str) -> float:
        return await self.evaluate("persuasion", argument)

    async def evaluate_cultural_acceptance(self, argument: str) -> float:
        return await self.evaluate("cultural_acceptance", argument)

    async def evaluate_factual_accuracy(self, argument: str) -> float:
        return await self.evaluate("factual_accuracy", argument)
