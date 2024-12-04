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
    async def traverse_debate(self, topic: str, max_depth: int):
        logger.info(f"Starting debate traversal for topic: {topic}")
        traverse_command = self.injector.get("traverse_debate_command")
        await traverse_command.execute(topic, max_depth)

    @log_execution_time
    async def submit_argument(self, argument, category):
        logger.info(f"Submitting argument in category: {category}")
        submit_argument_command = self.injector.get("submit_argument_command")
        await submit_argument_command.execute(argument, category)

    @log_execution_time
    async def generate_arguments(self, topic, subcategory, support, against):
        logger.info(
            f"Generating arguments for topic: {topic}, subcategory: {subcategory} supporting_prompt: {support}, against_prompt: {against}"
        )
        generate_arguments_command = self.injector.get("generate_arguments_command")
        await generate_arguments_command.execute(topic, subcategory, support, against)

    @log_execution_time
    async def evaluate_arguments(self, arguments):
        logger.info(f"Evaluating {len(arguments)} arguments")
        evaluate_arguments_command = self.injector.get("evaluate_arguments_command")
        await evaluate_arguments_command.execute(arguments)

    @log_execution_time
    async def load_file(self, file_path: str):
        logger.info(f"Loading arguments from file: {file_path}")
        load_file_command = self.injector.get("load_file_command")
        await load_file_command.execute(file_path)
