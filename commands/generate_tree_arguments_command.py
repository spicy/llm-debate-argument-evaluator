"""
TODO: This module...
"""

from features.argument_generation.argument_generation_service import (
    ArgumentGenerationService,
)
from infrastructure import AsyncProcessingService
from utils.logger import log_execution_time, logger


class GenerateTreeArgumentsCommand:
    def __init__(
        self,
        argument_generation_service: ArgumentGenerationService,
        async_processing_service: AsyncProcessingService,
    ):
        """TODO: Add Simple Docstring"""
        self.argument_generation_service = argument_generation_service
        self.async_service = async_processing_service

    @log_execution_time
    async def execute(
        self, node_argument: str, topic: str, category: str, num_arguments: int
    ) -> list:
        """Generates supporting and opposing arguments for a given node"""
        logger.info(f"Generating tree arguments for: {node_argument[:50]}...")

        arguments = await self.argument_generation_service.generate_arguments(
            topic=topic,
            subcategory=category,
            argument_text=node_argument,
            num_arguments=num_arguments,
        )

        logger.info(f"Generated {len(arguments)} arguments")
        return arguments
