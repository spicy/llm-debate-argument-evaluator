from abc import ABC, abstractmethod

from utils.logger import log_execution_time


class BaseLLMModel(ABC):
    @abstractmethod
    @log_execution_time
    async def evaluate_coherence(self, argument: str) -> float:
        pass

    @abstractmethod
    @log_execution_time
    async def evaluate_persuasion(self, argument: str) -> float:
        pass

    @abstractmethod
    @log_execution_time
    async def evaluate_cultural_acceptance(self, argument: str) -> float:
        pass

    @abstractmethod
    @log_execution_time
    async def evaluate_factual_accuracy(self, argument: str) -> float:
        pass
