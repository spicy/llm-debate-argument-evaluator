from user_interactions import UserInteractions

from utils.logger import log_execution_time, logger


class Controller:
    def __init__(self, injector, quit_event):
        self.injector = injector
        self.user_interactions = UserInteractions(self)
        self.quit_event = quit_event

    @log_execution_time
    async def start(self):
        await self.user_interactions.main_loop()

    @log_execution_time
    async def expand_node(self, node_id):
        logger.info(f"Expanding node: {node_id}")
        expand_node_command = self.injector.get("expand_node_command")
        await expand_node_command.execute(node_id)

    @log_execution_time
    async def submit_argument(self, argument, category):
        logger.info(f"Submitting argument in category: {category}")
        submit_argument_command = self.injector.get("submit_argument_command")
        await submit_argument_command.execute(argument, category)

    @log_execution_time
    async def generate_arguments(self, topic, subcategory):
        logger.info(
            f"Generating arguments for topic: {topic}, subcategory: {subcategory}"
        )
        generate_arguments_command = self.injector.get("generate_arguments_command")
        await generate_arguments_command.execute(topic, subcategory)

    @log_execution_time
    async def evaluate_arguments(self, arguments):
        logger.info(f"Evaluating {len(arguments)} arguments")
        evaluate_arguments_command = self.injector.get("evaluate_arguments_command")
        await evaluate_arguments_command.execute(arguments)
