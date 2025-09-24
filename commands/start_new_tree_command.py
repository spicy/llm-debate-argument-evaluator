"""
StartNewTreeCommand - Starts building an argument tree on the current tree.

This command creates a root node and begins the automated tree expansion
process for the currently selected tree.
"""

import asyncio

from commands.create_root_node_command import CreateRootNodeCommand
from commands.evaluate_node_command import EvaluateNodeCommand
from commands.expand_node_command import ExpandNodeCommand
from commands.build_tree_command import BuildTreeCommand
from features.tree.multi_tree_state_service import MultiTreeStateService
from infrastructure import AsyncProcessingService
from utils.logger import logger


class StartNewTreeCommand:
    def __init__(
        self,
        create_root_command: CreateRootNodeCommand,
        expand_node_command: ExpandNodeCommand,
        evaluate_tree_command: EvaluateNodeCommand,
        traverse_command: BuildTreeCommand,
        async_processing_service: AsyncProcessingService,
        tree_state_service: MultiTreeStateService,
    ):
        """
        Initialize the command with required services.

        Args:
            create_root_command: Command to create root nodes
            expand_node_command: Command to expand nodes
            evaluate_tree_command: Command to evaluate nodes
            traverse_command: Command to build/traverse trees
            async_processing_service: Service for async processing
            tree_state_service: Multi-tree state service
        """
        self.create_root_command = create_root_command
        self.expand_node_command = expand_node_command
        self.evaluate_tree_command = evaluate_tree_command
        self.traverse_command = traverse_command
        self.async_service = async_processing_service
        self.tree_state_service = tree_state_service

    async def _evaluation_worker(self):
        """Worker to process evaluation queue"""
        while True:
            node = await self.async_service.evaluation_queue.get()
            try:
                await self.evaluate_tree_command.execute(node["id"])
                # After evaluation, queue for traversal to see if new paths open up
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
                await self.traverse_command.execute(node_id, max_depth)
            except Exception as e:
                logger.error(f"Error traversing from node {node_id}: {str(e)}")
            finally:
                self.async_service.traversal_queue.task_done()

    async def execute(self, topic: str = None, max_depth: int = 3):
        """
        Start a complete tree generation and traversal process on the current tree.

        Args:
            topic: The topic for the tree's root node. If None, uses the tree's topic.
            max_depth: Maximum depth for tree expansion

        Returns:
            Root node ID if successful, None otherwise
        """
        # Ensure a tree is currently selected
        if not self.tree_state_service.has_current_tree:
            logger.error("No tree currently selected. Cannot start tree process.")
            return None

        current_tree = self.tree_state_service.current_tree

        # Use tree topic as default if no topic provided
        if topic is None:
            topic = current_tree.topic
            logger.info(f"Using tree topic '{topic}' for root node")

        logger.info(
            f"Starting tree process for topic '{topic}' in tree: {current_tree.display_name}"
        )

        # Start workers
        eval_worker_task = asyncio.create_task(self._evaluation_worker())
        trav_worker_task = asyncio.create_task(self._traversal_worker(max_depth))

        try:
            # Create and expand root node
            root_node_id = await self.create_root_command.execute(topic)
            if not root_node_id:
                logger.error("Failed to create root node. Aborting process.")
                return None

            logger.info(f"Created root node: {root_node_id}")

            await self.expand_node_command.execute(int(root_node_id))
            logger.info("Expanded root node")

            # Wait for all tasks to be processed
            await self.async_service.evaluation_queue.join()
            await self.async_service.traversal_queue.join()

            logger.info("Completed tree process")

            # Final traversal to find the best path
            await self.traverse_command.execute(root_node_id, max_depth)

            return root_node_id

        except Exception as e:
            logger.error(f"Error during tree process: {str(e)}", exc_info=True)
            return None
        finally:
            # Shutdown workers
            eval_worker_task.cancel()
            trav_worker_task.cancel()
            await asyncio.gather(
                eval_worker_task, trav_worker_task, return_exceptions=True
            )
            logger.info("Tree workers have been shut down.")
