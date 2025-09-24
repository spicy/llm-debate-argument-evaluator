"""
Tree pruning command - Removes low-quality branches from the debate tree.
"""

from typing import Dict, List, Set, Optional
from features.tree.multi_tree_state_service import MultiTreeStateService
from features.tree.tree_repository import TreeRepository
from config.tree_config import tree_config
from utils.logger import logger


class PruneTreeCommand:
    def __init__(
        self,
        tree_state_service: MultiTreeStateService,
        repository: TreeRepository,
    ):
        """
        Initialize the prune command.

        Args:
            tree_state_service: Multi-tree state service for tree operations
            repository: Repository for database operations
        """
        self.tree_state_service = tree_state_service
        self.repository = repository

    async def execute(self, score_threshold: Optional[float] = None) -> int:
        """
        Prune the tree by removing nodes with low-quality paths.

        Uses path-based pruning: removes nodes whose best possible path
        to any leaf is below the threshold score.

        Args:
            score_threshold: Minimum average path score to keep (0.0 to 1.0).
                           If None, uses config default or prompts user.

        Returns:
            Number of nodes removed
        """
        if not self.tree_state_service.has_current_tree:
            logger.error("No tree currently selected for pruning")
            return 0

        # Determine threshold from config or parameter
        if score_threshold is None:
            score_threshold = tree_config.DEFAULT_PRUNE_THRESHOLD

        # Check if we should use config default or prompt user
        if score_threshold is None or score_threshold < 0:
            # This should not happen since UI always provides threshold
            # But handle gracefully just in case
            logger.error("No valid pruning threshold provided")
            return 0

        # Validate threshold bounds
        score_threshold = max(
            tree_config.MIN_PRUNE_THRESHOLD,
            min(tree_config.MAX_PRUNE_THRESHOLD, score_threshold),
        )

        logger.info(f"Starting tree pruning with threshold {score_threshold:.2f}")

        # Get all nodes (excluding root from scoring calculations)
        all_nodes = self.tree_state_service.get_all_nodes()
        if not all_nodes:
            logger.info("No nodes to prune")
            return 0

        # Build node relationships
        nodes_map = {node["id"]: node for node in all_nodes}

        # Find nodes to remove using path-based analysis
        nodes_to_remove = self._find_nodes_to_prune(
            all_nodes, nodes_map, score_threshold
        )

        if not nodes_to_remove:
            logger.info("No nodes meet pruning criteria")
            return 0

        # Remove nodes from database and memory
        removed_count = await self._remove_nodes(nodes_to_remove)

        logger.info(f"Pruning complete: removed {removed_count} nodes")
        return removed_count

    def _find_nodes_to_prune(
        self, all_nodes: List[Dict], nodes_map: Dict[int, Dict], threshold: float
    ) -> Set[int]:
        """
        Find nodes to prune using path-based analysis.

        Args:
            all_nodes: List of all nodes in tree
            nodes_map: Map of node_id -> node_data
            threshold: Score threshold for pruning

        Returns:
            Set of node IDs to remove
        """
        nodes_to_remove = set()

        # For each non-root node, calculate its best possible path score
        for node in all_nodes:
            node_id = node["id"]

            # Never prune root nodes
            if node.get("argument_type") == "root":
                continue

            # Calculate best path score from this node to any leaf
            best_path_score = self._calculate_best_path_from_node(node_id, nodes_map)

            # If best possible path is below threshold, mark for removal
            if best_path_score < threshold:
                nodes_to_remove.add(node_id)
                logger.debug(
                    f"Marking node {node_id} for pruning (best path score: {best_path_score:.3f})"
                )

        # Remove children of pruned nodes to avoid orphans
        nodes_to_remove = self._include_descendant_nodes(nodes_to_remove, nodes_map)

        return nodes_to_remove

    def _calculate_best_path_from_node(
        self, start_node_id: int, nodes_map: Dict[int, Dict]
    ) -> float:
        """
        Calculate the best possible path score from a node to any leaf.

        Uses recursive traversal to find the highest-scoring path.
        """
        start_node = nodes_map.get(start_node_id)
        if not start_node:
            return 0.0

        # Find all leaf nodes reachable from this node
        reachable_leaves = self._find_reachable_leaves(start_node_id, nodes_map)

        if not reachable_leaves:
            # This node is a leaf itself
            return self._get_node_score(start_node)

        best_score = -float("inf")

        # Calculate path score to each reachable leaf
        for leaf_id in reachable_leaves:
            path_score = self._calculate_path_score(start_node_id, leaf_id, nodes_map)
            best_score = max(best_score, path_score)

        return best_score

    def _find_reachable_leaves(
        self, node_id: int, nodes_map: Dict[int, Dict]
    ) -> Set[int]:
        """Find all leaf nodes reachable from the given node."""
        leaves = set()
        children = [
            n["id"] for n in nodes_map.values() if n.get("parent_id") == node_id
        ]

        if not children:
            # This is a leaf
            leaves.add(node_id)
        else:
            # Recursively find leaves in subtrees
            for child_id in children:
                leaves.update(self._find_reachable_leaves(child_id, nodes_map))

        return leaves

    def _calculate_path_score(
        self, start_id: int, end_id: int, nodes_map: Dict[int, Dict]
    ) -> float:
        """Calculate average score of path from start to end node."""
        path = []
        current_id = end_id

        # Build path from end to start
        while current_id is not None and current_id in nodes_map:
            current_node = nodes_map[current_id]
            path.append(current_node)

            if current_id == start_id:
                break

            current_id = current_node.get("parent_id")

        if not path:
            return 0.0

        # Calculate average score excluding root nodes
        total_score = 0.0
        scored_nodes = 0

        for node in path:
            if node.get("argument_type") != "root":
                total_score += self._get_node_score(node)
                scored_nodes += 1

        return total_score / scored_nodes if scored_nodes > 0 else 0.0

    def _get_node_score(self, node: Dict) -> float:
        """Extract score from node evaluation."""
        evaluation = node.get("evaluation", {})
        if isinstance(evaluation, dict):
            return evaluation.get("average", 0.0)
        elif isinstance(evaluation, (int, float)):
            return float(evaluation)
        return 0.0

    def _include_descendant_nodes(
        self, nodes_to_remove: Set[int], nodes_map: Dict[int, Dict]
    ) -> Set[int]:
        """Include all descendants of nodes marked for removal."""
        expanded_removal_set = nodes_to_remove.copy()

        # Keep adding descendants until no new ones found
        while True:
            new_nodes = set()
            for node in nodes_map.values():
                parent_id = node.get("parent_id")
                if parent_id in expanded_removal_set:
                    new_nodes.add(node["id"])

            if not new_nodes - expanded_removal_set:
                break  # No new descendants found

            expanded_removal_set.update(new_nodes)

        return expanded_removal_set

    async def _remove_nodes(self, node_ids: Set[int]) -> int:
        """Remove nodes from database and update in-memory state."""
        removed_count = 0
        tree_id = self.tree_state_service.current_tree_id

        for node_id in node_ids:
            try:
                # Remove from database
                success = self.repository.delete_node(node_id, tree_id)
                if success:
                    # Remove from memory
                    if str(node_id) in self.tree_state_service.tree:
                        del self.tree_state_service.tree[str(node_id)]
                    removed_count += 1
                    logger.debug(f"Removed node {node_id}")
                else:
                    logger.warning(f"Failed to remove node {node_id} from database")

            except Exception as e:
                logger.error(f"Error removing node {node_id}: {e}")

        # Notify observers of tree changes
        await self.tree_state_service.notify(
            self.tree_state_service.tree, self.tree_state_service.optimal_path
        )

        return removed_count
