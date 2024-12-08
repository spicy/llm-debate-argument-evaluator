from commands.create_root_node_command import CreateRootNodeCommand
from commands.evaluate_debate_tree_command import EvaluateDebateTreeCommand
from commands.expand_node_command import ExpandNodeCommand
from commands.traverse_debate_command import TraverseDebateCommand
from utils.logger import log_execution_time, logger


class RunDebateTreeCommand:
    def __init__(
        self,
        create_root_command: CreateRootNodeCommand,
        expand_node_command: ExpandNodeCommand,
        evaluate_tree_command: EvaluateDebateTreeCommand,
        traverse_command: TraverseDebateCommand,
    ):
        self.create_root_command = create_root_command
        self.expand_node_command = expand_node_command
        self.evaluate_tree_command = evaluate_tree_command
        self.traverse_command = traverse_command

    @log_execution_time
    async def execute(self, topic: str, max_depth: int = 3):
        """Runs a complete debate tree generation and traversal"""
        try:
            logger.info(f"Starting complete debate tree process for topic: {topic}")

            # Step 1: Create root node
            root_node_id = await self.create_root_command.execute(topic)
            logger.info(f"Created root node: {root_node_id}")

            # Step 2: Expand root node (More explicitly, expand the root node and evaluate it)
            await self.expand_node_command.execute(root_node_id)
            logger.info("Expanded root node")

            # Expand node already evaluates the node, so we can skip this step
            # # Step 3: Evaluate the tree
            # await self.evaluate_tree_command.execute()
            # logger.info("Evaluated debate tree")

            # Step 4: Traverse the tree
            await self.traverse_command.execute(root_node_id, max_depth)
            logger.info("Completed debate tree traversal")

            return root_node_id

        except Exception as e:
            logger.error(f"Error during debate tree process: {str(e)}")
            raise
