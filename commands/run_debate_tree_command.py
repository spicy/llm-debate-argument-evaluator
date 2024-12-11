import asyncio

from commands.create_root_node_command import CreateRootNodeCommand
from commands.evaluate_debate_tree_command import EvaluateDebateTreeCommand
from commands.expand_node_command import ExpandNodeCommand
from commands.traverse_debate_command import TraverseDebateCommand
from services.async_processing_service import AsyncProcessingService
from utils.logger import log_execution_time, logger


class RunDebateTreeCommand:
    def __init__(
        self,
        create_root_command: CreateRootNodeCommand,
        expand_node_command: ExpandNodeCommand,
        evaluate_tree_command: EvaluateDebateTreeCommand,
        traverse_command: TraverseDebateCommand,
        async_processing_service: AsyncProcessingService,
    ):
        self.create_root_command = create_root_command
        self.expand_node_command = expand_node_command
        self.evaluate_tree_command = evaluate_tree_command
        self.traverse_command = traverse_command
        self.async_service = async_processing_service

    async def _evaluation_worker(self):
        """Worker to process evaluation queue"""
        while True:
            node = await self.async_service.evaluation_queue.get()
            try:
                await self.async_service.process_async(
                    self.evaluate_tree_command.execute_single_node(node["id"])
                )
                await self.async_service.queue_traversal(node["id"])
            except Exception as e:
                logger.error(f"Error evaluating node {node['id']}: {str(e)}")
            finally:
                self.async_service.evaluation_queue.task_done()

    async def _traversal_worker(self, max_depth: int):
        """Worker to process traversal queue"""
        while True:
            node_id = await self.async_service.traversal_queue.get()
            try:
                await self.async_service.process_async(
                    self.traverse_command.execute(node_id, max_depth)
                )
            except Exception as e:
                logger.error(f"Error traversing from node {node_id}: {str(e)}")
            finally:
                self.async_service.traversal_queue.task_done()

    @log_execution_time
    async def execute(self, topic: str, max_depth: int = 3):
        """Runs a complete debate tree generation and traversal"""
        try:
            logger.info(f"Starting complete debate tree process for topic: {topic}")

            # Start workers as tasks
            evaluation_worker = await self.async_service.process_async(
                self._evaluation_worker()
            )
            traversal_worker = await self.async_service.process_async(
                self._traversal_worker(max_depth)
            )

            # Create and expand root node
            root_node_id = await self.create_root_command.execute(topic)
            logger.info(f"Created root node: {root_node_id}")

            await self.expand_node_command.execute(root_node_id)
            logger.info("Expanded root node")

            # Wait for initial evaluation and traversal
            await self.async_service.evaluation_queue.join()
            await self.async_service.traversal_queue.join()

            # Cancel worker tasks
            evaluation_worker.cancel()
            traversal_worker.cancel()

            try:
                await evaluation_worker
                await traversal_worker
            except asyncio.CancelledError:
                pass

            logger.info("Completed debate tree process")
            return root_node_id

        except Exception as e:
            logger.error(f"Error during debate tree process: {str(e)}")
            raise
