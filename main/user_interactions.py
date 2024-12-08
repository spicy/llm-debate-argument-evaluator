import asyncio

from utils.logger import logger


class UserInteractions:
    def __init__(self, controller):
        self.controller = controller

    async def main_loop(self):
        while not self.controller.quit_event.is_set():
            command = await asyncio.to_thread(
                input,
                "Enter a command (run/traverse/expand/submit/generate/evaluate/load/quit): ",
            )

            if command == "quit":
                logger.info("User requested to quit")
                self.controller.quit_event.set()
                break
            elif command == "run":
                topic = await asyncio.to_thread(input, "Enter topic for debate tree: ")
                depth = await asyncio.to_thread(
                    input, "Enter maximum depth (default 3): "
                )
                await self.controller.run_debate_tree(topic, int(depth) if depth else 3)
            elif command == "traverse":
                topic = await asyncio.to_thread(input, "Enter root topic to traverse: ")
                depth = await asyncio.to_thread(
                    input, "Enter maximum depth (default 3): "
                )
                await self.controller.traverse_debate(topic, int(depth) if depth else 3)
            elif command == "expand":
                node_id = await asyncio.to_thread(input, "Enter node ID to expand: ")
                logger.info(f"User requested to expand node: {node_id}")
                await self.controller.expand_node(node_id)
            elif command == "submit":
                argument = await asyncio.to_thread(input, "Enter your argument: ")
                category = await asyncio.to_thread(input, "Enter category: ")
                logger.info(f"User submitted argument in category: {category}")
                await self.controller.submit_argument(argument, category)
            elif command == "generate":
                topic = await asyncio.to_thread(input, "Enter topic: ")
                subcategory = await asyncio.to_thread(input, "Enter subcategory: ")
                support = await asyncio.to_thread(
                    input, "Enter supporting prompt (optional): "
                )
                against = await asyncio.to_thread(
                    input, "Enter against prompt (optional): "
                )
                logger.info(
                    f"User requested argument generation for topic: {topic}, subcategory: {subcategory}"
                )
                await self.controller.generate_arguments(
                    topic, subcategory, support, against
                )
            elif command == "evaluate":
                logger.info("User requested to evaluate arguments")
                await self.controller.evaluate_debate_tree()
                # arguments = []
                # while True:
                #     arg = await asyncio.to_thread(
                #         input,
                #         "Enter argument (or empty line to finish): ",
                #     )
                #     if not arg:
                #         break
                #     arguments.append(arg)
                # logger.info(f"User requested evaluation of {len(arguments)} arguments")
                # await self.controller.evaluate_arguments(arguments)
            elif command == "load":
                file_path = await asyncio.to_thread(
                    input, "Enter the path to the JSON file: "
                )
                logger.info(f"User requested to load file: {file_path}")
                await self.controller.load_file(file_path)
            else:
                logger.warning(f"Unknown command: {command}")
