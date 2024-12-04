import asyncio

from utils.logger import logger


class UserInteractions:
    def __init__(self, controller):
        self.controller = controller

    async def main_loop(self):
        logger.info("Starting main interaction loop")
        while not asyncio.Event.is_set(self.controller.quit_event):
            command = await asyncio.to_thread(
                input, "Enter a command (expand/submit/generate/evaluate/show/quit): "
            )
            command = command.lower()

            if command == "quit":
                self.controller.quit_event.set()
                break
            elif command == "expand":
                node_id = await asyncio.to_thread(input, "Enter node ID to expand or \"top\" to expand top node: ")
                logger.info(f"User requested to expand node: {node_id}")
                await self.controller.expand_node(node_id)
            elif command == "submit":
                argument = await asyncio.to_thread(input, "Enter your argument: ")
                category = await asyncio.to_thread(input, "Enter the category: ")
                logger.info(f"User submitted argument in category: {category}")
                await self.controller.submit_argument(argument, category)
            elif command == "generate":
                topic = await asyncio.to_thread(input, "Enter the debate topic: ")
                subcategory = await asyncio.to_thread(input, "Enter the subcategory: ")
                support = await asyncio.to_thread(
                    input,
                    f"Provide a prompt that supports {subcategory} in terms of {topic}:",
                )
                against = await asyncio.to_thread(
                    input,
                    f"Provide a prompt that is against {subcategory} in terms of {topic}:",
                )
                logger.info(
                    f"User requested to generate arguments for topic: {topic}, subcategory: {subcategory}, support: {support}, against: {against}"
                )
                await self.controller.generate_arguments(
                    topic, subcategory, support, against
                )
            elif command == "evaluate":
                arguments = await asyncio.to_thread(
                    input, "Enter arguments to evaluate (comma-separated): "
                )
                arguments = arguments.split(",")
                logger.info(f"User requested to evaluate {len(arguments)} arguments")
                await self.controller.evaluate_arguments(arguments)
            elif command == "list":
                logger.info(F"Showing the nodescores dipslay")
            else:
                logger.warning(f"User entered invalid command: {command}")
                logger.info("Invalid command. Please try again.")

        logger.info("User requested to quit the application")
