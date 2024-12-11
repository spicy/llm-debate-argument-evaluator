from services.argument_generation_service import ArgumentGenerationService
from services.async_processing_service import AsyncProcessingService
from utils.logger import log_execution_time, logger


class GenerateDebateArgumentsCommand:
    def __init__(
        self,
        argument_generation_service: ArgumentGenerationService,
        async_processing_service: AsyncProcessingService,
    ):
        self.argument_generation_service = argument_generation_service
        self.async_service = async_processing_service

    @log_execution_time
    async def execute(self, node_argument: str, category: str) -> list:
        """Generates supporting and opposing arguments for a given node"""
        logger.info(f"Generating debate arguments for: {node_argument[:50]}...")

        # Create prompts
        support_prompt = f"Based on this argument: {node_argument}, make an argument that supports it further."
        against_prompt = f"Based on this argument: {node_argument}, make an argument that rebuttals this argument."

        # Process argument generation asynchronously
        generation_task = await self.async_service.process_async(
            self.argument_generation_service.generate_arguments(
                "none", category, support_prompt, against_prompt, 1
            )
        )

        arguments = await generation_task
        logger.info(f"Generated {len(arguments)} arguments")
        return arguments
