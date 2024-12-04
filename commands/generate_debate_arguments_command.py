from services.argument_generation_service import ArgumentGenerationService
from utils.logger import log_execution_time, logger


class GenerateDebateArgumentsCommand:
    def __init__(self, argument_generation_service: ArgumentGenerationService):
        self.argument_generation_service = argument_generation_service

    @log_execution_time
    async def execute(self, node_argument: str, category: str) -> list:
        """Generates supporting and opposing arguments for a given node"""
        logger.info(f"Generating debate arguments for: {node_argument[:50]}...")

        support_prompt = f"Based on this argument: {node_argument}, make an argument that supports it further."
        against_prompt = f"Based on this argument: {node_argument}, make an argument that rebuttals this argument."

        arguments = await self.argument_generation_service.generate_arguments(
            "none", category, support_prompt, against_prompt, 1
        )

        logger.info(f"Generated {len(arguments)} arguments")
        return arguments
