import asyncio
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from controller import Controller
from dependency_injector import DependencyInjector

from config.logger_config import logger_config
from utils.logger import logger

async def main():
    logger.info("Starting the LLM Debate Argument Evaluator")
    # Initialize dependency injector
    injector = DependencyInjector()
    injector.initialize_dependencies()

    # Setup quit_event handler for both
    quit_event = asyncio.Event()

    # Get renderer(pygame)
    renderer = injector.get("modified_renderer")

    # Create controller
    controller = Controller(injector, quit_event)

    # Start the application
    await asyncio.gather(
        controller.start(),
        renderer.start(quit_event)
    )
    logger.info("LLM Debate Argument Evaluator finished")


if __name__ == "__main__":
    asyncio.run(main())
