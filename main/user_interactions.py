from utils.logger import logger


class UserInteractions:
    def __init__(self, controller):
        self.controller = controller

    async def main_loop(self):
        logger.info("Starting main interaction loop")
        while True:
            command = input(
                "Enter a command (expand/submit/generate/evaluate/quit): "
            ).lower()

            if command == "quit":
                logger.info("User requested to quit the application")
                break
            elif command == "expand":
                node_id = input("Enter node ID to expand: ")
                logger.info(f"User requested to expand node: {node_id}")
                await self.controller.expand_node(node_id)
            elif command == "submit":
                argument = input("Enter your argument: ")
                category = input("Enter the category: ")
                logger.info(f"User submitted argument in category: {category}")
                await self.controller.submit_argument(argument, category)
            elif command == "generate":
                topic = input("Enter the debate topic: ")
                subcategory = input("Enter the subcategory: ")
                support = input(f"Provide a prompt that supports {subcategory} in terms of {topic}:")
                against = input(f"Provide a prompt that is against {subcategory} in terms of {topic}:")
                logger.info(
                    f"User requested to generate arguments for topic: {topic}, subcategory: {subcategory}, support: {support}, against: {against}"
                )
                await self.controller.generate_arguments(topic, subcategory, support, against)
            elif command == "evaluate":
                arguments = input(
                    "Enter arguments to evaluate (comma-separated): "
                ).split(",")
                logger.info(f"User requested to evaluate {len(arguments)} arguments")
                await self.controller.evaluate_arguments(arguments)
            else:
                logger.warning(f"User entered invalid command: {command}")
                logger.info("Invalid command. Please try again.")
