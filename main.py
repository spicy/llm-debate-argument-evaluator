"""
TODO: This module...
"""

import asyncio
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from core.controller import Controller
from core.dependency_injector import DependencyInjector
from core.user_interactions import UserInteractions
from utils.logger import setup_logger, logger
from config.visualization_config import visualization_config


async def main():
    """Initializes and runs the application."""
    injector = DependencyInjector()
    user_interactions = UserInteractions()

    renderer_type = user_interactions.get_renderer_type()

    injector.initialize_dependencies(renderer_type=renderer_type)

    quit_event = asyncio.Event()
    controller = Controller(injector.registry, quit_event, user_interactions)
    user_interactions.initialize_commands(controller)

    renderer = injector.registry.get("renderer")

    try:
        # Start the renderer if it has a continuous loop
        renderer_task = None
        if hasattr(renderer, "start"):
            # Run the async renderer as a proper task
            renderer_task = asyncio.create_task(renderer.start(quit_event))

        # Start the main application loop (includes tree selection)
        await user_interactions.main_loop()

    finally:
        # Ensure cleanup is called
        if renderer_task:
            quit_event.set()
            await renderer_task
        if hasattr(renderer, "cleanup"):
            renderer.cleanup()
        logger.info("Application shut down gracefully.")


if __name__ == "__main__":
    setup_logger()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user. Shutting down.")
    except Exception as e:
        logger.error(f"An unhandled exception occurred: {e}", exc_info=True)
