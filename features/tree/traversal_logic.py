"""
TraversalLogic - Implements Monte Carlo Tree Search with UCB1 algorithm.

This module provides a complete MCTS implementation for debate argument trees,
including proper UCB1 node selection, tree traversal, and backpropagation.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, AsyncGenerator, Callable, Awaitable

from features.tree.tree_data_service import TreeDataService
from utils.logger import logger


class TraversalLogic:
    def __init__(
        self,
        data_service: TreeDataService,
        exploration_weight: float = 2.0,
    ):
        """
        Initialize the traversal logic with MCTS parameters.

        Args:
            data_service: Service for accessing tree data
            exploration_weight: UCB1 exploration parameter (typically sqrt(2))
        """
        self.data_service = data_service
        self.exploration_weight = exploration_weight
        self.repository = getattr(
            data_service, "repository", None
        )  # For backward compatibility
        logger.info(
            f"TraversalLogic initialized with exploration_weight={exploration_weight}"
        )

    async def traverse(
        self,
        start_node_id: int,
        expand_node_func: Callable[[int], Awaitable[List[Dict]]],
        max_depth: int,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute MCTS traversal starting from a given node.

        Args:
            start_node_id: ID of the selected node to start traversal from
            expand_node_func: Function to expand nodes (create children)
            max_depth: Maximum depth relative to the selected node

        Yields:
            Information about each traversal iteration
        """
        iteration = 0
        max_iterations = 100  # Prevent infinite loops

        # Get the selected node's depth to make max_depth relative
        selected_start_node = self.data_service.get_node(str(start_node_id))
        selected_depth = (
            selected_start_node.get("depth", 0) if selected_start_node else 0
        )
        absolute_max_depth = selected_depth + max_depth

        # Store the start node for use in node selection
        self._traversal_start_node_id = start_node_id
        self._traversal_start_node = selected_start_node

        logger.info(
            f"Starting MCTS traversal from selected node {start_node_id} at depth {selected_depth}, "
            f"max_relative_depth={max_depth}, absolute_max_depth={absolute_max_depth}"
        )

        while iteration < max_iterations:
            iteration += 1

            # MCTS Phase 1: Selection - Find the best leaf node to expand
            selected_node, path = self._select_node_for_expansion()
            if not selected_node:
                logger.info("No more nodes to expand, traversal complete")
                break

            # Check depth limit (relative to selected node)
            current_depth = selected_node.get("depth", 0)
            if current_depth >= absolute_max_depth:
                relative_depth = current_depth - selected_depth
                logger.info(
                    f"Reached maximum relative depth {relative_depth} (absolute depth {current_depth}), stopping traversal"
                )
                break

            # MCTS Phase 2: Expansion - Create child nodes
            logger.debug(
                f"Iteration {iteration}: Expanding node {selected_node['id']} at depth {current_depth}"
            )
            new_children = await expand_node_func(selected_node["id"])

            # MCTS Phase 3: Evaluation - Child nodes are evaluated during expansion
            # MCTS Phase 4: Backpropagation - Update statistics up the tree
            if new_children:
                # Visit the selected node (increment its visits)
                await self._update_node_visits(selected_node["id"], path)

                # Backpropagate results for each new child
                for child in new_children:
                    await self._backpropagate_results(child, path + [selected_node])
            else:
                # No children created, just increment visits for selected node
                await self._increment_node_visits(selected_node["id"])

            yield {
                "iteration": iteration,
                "node_expanded": selected_node["id"],
                "children_created": len(new_children) if new_children else 0,
                "current_depth": current_depth,
            }

        logger.info(
            f"MCTS traversal completed after {iteration} iterations (started from selected node at depth {selected_depth})"
        )

    def _select_node_for_expansion(
        self,
    ) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Select the best node for expansion using UCB1 and return the path to it.

        Uses the traversal start node as the root for selection, not the tree's root.

        Returns:
            Tuple of (selected_node, path_to_node)
        """
        # Use the start node specified for this traversal, not the tree's root
        if not hasattr(self, "_traversal_start_node") or not self._traversal_start_node:
            logger.error(
                "No traversal start node set. Cannot select node for expansion."
            )
            return None, []

        # Select the most promising leaf node using UCB1, starting from the specified node
        logger.debug(
            f"Starting node selection from traversal root: {self._traversal_start_node['id']}"
        )
        selected_node, path = self._select_promising_leaf(self._traversal_start_node)
        if selected_node:
            logger.debug(
                f"Selected node {selected_node['id']} for expansion (path length: {len(path)})"
            )
        return selected_node, path

    def _select_promising_leaf(
        self, root_node: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Select the most promising leaf node to expand using UCB1 traversal.

        Args:
            root_node: The root node to start selection from

        Returns:
            Tuple of (leaf_node, path_to_leaf)
        """
        current_node = root_node
        path = []

        while True:
            path.append(current_node)
            children = self.data_service.get_children(str(current_node["id"]))

            if not children:
                # This is a leaf node
                return current_node, path[:-1]  # Don't include the leaf in its own path

            # Select the best child using UCB1
            best_child = max(children, key=lambda c: self._calculate_ucb1_score(c))
            current_node = best_child

    def _calculate_ucb1_score(self, node: Dict[str, Any]) -> float:
        """Calculates the UCB1 score for a node."""
        if node.get("visits", 0) == 0:
            return float("inf")  # Prioritize unvisited nodes

        wins = node.get("wins", 0.0)
        visits = node.get("visits", 1)
        parent_id = node.get("parent_id")
        if not parent_id:
            return wins / visits  # Root node case

        parent = self.data_service.get_node(str(parent_id))
        parent_visits = parent.get("visits", 1) if parent else 1

        exploitation_term = wins / visits
        exploration_term = self.exploration_weight * math.sqrt(
            math.log(parent_visits) / visits
        )
        return exploitation_term + exploration_term

    async def _update_node_visits(
        self, node_id: int, path: List[Dict[str, Any]]
    ) -> None:
        """
        Update visit count for a node and all nodes in its path.

        Args:
            node_id: ID of the node that was visited
            path: Path of nodes leading to this node
        """
        # Update the selected node
        await self._increment_node_visits(node_id)

        # Update all nodes in the path leading to this node
        for node in path:
            await self._increment_node_visits(node["id"])

    async def _increment_node_visits(self, node_id: int) -> None:
        """
        Increment the visit count for a specific node.

        Args:
            node_id: ID of the node to increment visits for
        """
        try:
            # Get current node data
            current_node = self.data_service.get_node(str(node_id))
            if not current_node:
                logger.warning(f"Cannot update visits for non-existent node {node_id}")
                return

            # Increment visits
            current_visits = current_node.get("visits", 0)
            new_visits = current_visits + 1

            # Update the node
            await self._update_node_data(node_id, {"visits": new_visits})
            logger.debug(
                f"Updated node {node_id} visits: {current_visits} -> {new_visits}"
            )

        except Exception as e:
            logger.error(f"Error incrementing visits for node {node_id}: {e}")

    async def _backpropagate_results(
        self, child_node: Dict[str, Any], path: List[Dict[str, Any]]
    ) -> None:
        """
        Backpropagate evaluation results up the tree to update win statistics.

        Args:
            child_node: The newly created child node with evaluation results
            path: Path of ancestor nodes to update
        """
        try:
            # Extract the child's evaluation score
            child_score = self._calculate_node_score(child_node)

            # Determine if this is a "win" (good score)
            is_win = child_score > 0.5  # Threshold for considering a result a "win"

            # Update wins for all ancestors in the path
            for ancestor in path:
                await self._update_node_wins(ancestor["id"], is_win, child_score)

            logger.debug(
                f"Backpropagated score {child_score:.3f} (win={is_win}) through {len(path)} ancestors"
            )

        except Exception as e:
            logger.error(
                f"Error during backpropagation for child {child_node.get('id', 'unknown')}: {e}"
            )

    async def _update_node_wins(self, node_id: int, is_win: bool, score: float) -> None:
        """
        Update the win statistics for a node based on a child's performance.

        Args:
            node_id: ID of the node to update
            is_win: Whether the result counts as a win
            score: The actual score value for more nuanced updates
        """
        try:
            # Get current node data
            current_node = self.data_service.get_node(str(node_id))
            if not current_node:
                logger.warning(f"Cannot update wins for non-existent node {node_id}")
                return

            # Get current wins (could be int or float)
            current_wins = float(current_node.get("wins", 0.0))

            # Update wins based on score (more nuanced than just binary win/loss)
            # Use score directly as a partial win (0.0 to 1.0)
            new_wins = current_wins + score

            # Alternative: Use binary win/loss
            # new_wins = current_wins + (1.0 if is_win else 0.0)

            # Update the node
            await self._update_node_data(node_id, {"wins": new_wins})
            logger.debug(
                f"Updated node {node_id} wins: {current_wins:.3f} -> {new_wins:.3f} (score: {score:.3f})"
            )

        except Exception as e:
            logger.error(f"Error updating wins for node {node_id}: {e}")

    async def _update_node_data(
        self, node_id: int, update_data: Dict[str, Any]
    ) -> None:
        """
        Update node data both in the repository and in-memory state.

        Args:
            node_id: ID of the node to update
            update_data: Dictionary of data to update
        """
        try:
            # The data_service should be MultiTreeStateService which has update_node method
            if hasattr(self.data_service, "update_node"):
                await self.data_service.update_node(str(node_id), update_data)
                logger.debug(f"Updated node {node_id} via data service")
            else:
                logger.warning(
                    f"Data service does not support update_node method for node {node_id}"
                )

        except Exception as e:
            logger.error(f"Error updating node {node_id} data: {e}")

    def find_optimal_path(self) -> Tuple[List[Dict[str, Any]], float]:
        """Finds the optimal path from the root to a leaf node by average score."""
        all_nodes = self.data_service.get_all_nodes()
        if not all_nodes:
            return [], -1.0

        nodes_map = {node["id"]: node for node in all_nodes}
        leaf_nodes = [
            node
            for node in all_nodes
            if not self.data_service.get_children(str(node["id"]))
        ]

        best_path = []
        best_score = -float("inf")

        for leaf in leaf_nodes:
            path = []
            current_node = leaf
            total_score = 0
            scored_nodes = 0  # Count only non-root nodes for averaging

            while current_node:
                path.append(current_node)
                # Exclude root nodes from score calculation as they represent topics, not arguments
                if current_node.get("argument_type") != "root":
                    total_score += self._calculate_node_score(current_node)
                    scored_nodes += 1
                parent_id = current_node.get("parent_id")
                if parent_id is None:
                    break
                current_node = nodes_map.get(parent_id)

            if not path or scored_nodes == 0:
                continue

            avg_score = (
                total_score / scored_nodes
            )  # Average only argument nodes, not root

            if avg_score > best_score:
                best_score = avg_score
                best_path = list(reversed(path))

        return best_path, best_score

    def _calculate_node_score(self, node: Dict[str, Any]) -> float:
        """Calculate the score of a single node based on its evaluation."""
        evaluation = node.get("evaluation", {})
        if isinstance(evaluation, dict):
            return evaluation.get("average", 0.0)
        elif isinstance(evaluation, (int, float)):
            return float(evaluation)
        return 0.0

    def log_optimal_path(
        self, optimal_path: List[Dict[str, Any]] = None, best_score: float = None
    ) -> None:
        """
        Logs the optimal path to the console.

        Args:
            optimal_path: Path to log, if None will calculate it
            best_score: Score of the path, if None will calculate it
        """
        # Calculate path if not provided
        if optimal_path is None or best_score is None:
            calculated_path, calculated_score = self.find_optimal_path()
            optimal_path = optimal_path or calculated_path
            best_score = best_score or calculated_score

        if not optimal_path:
            logger.info("No optimal path found to log.")
            return

        logger.info(f"\nOptimal tree path (best average score: {best_score:.2f}):")
        for i, node in enumerate(optimal_path):
            indent = "  " * i
            score = self._calculate_node_score(node)
            visits = node.get("visits", 0)
            wins = node.get("wins", 0.0)
            win_rate = (wins / visits) if visits > 0 else 0.0

            logger.info(
                f"{indent}+- Node {node['id']} (Score: {score:.2f}, Visits: {visits}, Win Rate: {win_rate:.2f})"
            )
            logger.info(f"{indent}|  Argument: {node['argument'][:100]}...")
