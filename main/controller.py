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
    async def create_root_node(self, topic: str) -> str:
        """Creates the root node for a debate tree"""
        logger.info(f"Creating root node for topic: {topic}")
        create_root_command = self.injector.get("create_root_node_command")
        return await create_root_command.execute(topic)

    @log_execution_time
    async def expand_node(self, node_id):
        logger.info(f"Expanding node: {node_id}")
        expand_node_command = self.injector.get("expand_node_command")
        await expand_node_command.execute(node_id)

    @log_execution_time
    async def evaluate_debate_tree(self):
        """Evaluates the entire debate tree"""
        logger.info("Starting debate tree evaluation")
        evaluate_command = self.injector.get("evaluate_debate_tree_command")
        await evaluate_command.execute()

    @log_execution_time
    async def traverse_debate(self, root_node_id: str, max_depth: int):
        """Traverses an existing debate tree"""
        logger.info("Starting debate traversal")
        traverse_command = self.injector.get("traverse_debate_command")
        await traverse_command.execute(root_node_id, max_depth)

    @log_execution_time
    async def submit_argument(self, argument, category):
        logger.info(f"Submitting argument in category: {category}")
        submit_argument_command = self.injector.get("submit_argument_command")
        await submit_argument_command.execute(argument, category)

    @log_execution_time
    async def generate_arguments(self, topic, subcategory, support, against):
        logger.info(f"Generating arguments for topic: {topic}")
        generate_command = self.injector.get("generate_debate_arguments_command")
        await generate_command.execute(topic, subcategory, support, against)

    @log_execution_time
    async def load_file(self, file_path: str):
        logger.info(f"Loading arguments from file: {file_path}")
        load_file_command = self.injector.get("load_file_command")
        await load_file_command.execute(file_path)

    @log_execution_time
    async def run_debate_tree(self, topic: str, max_depth: int = 3):
        """Runs the complete debate tree process"""
        logger.info(f"Running complete debate tree process for topic: {topic}")
        run_command = self.injector.get("run_debate_tree_command")
        return await run_command.execute(topic, max_depth)
