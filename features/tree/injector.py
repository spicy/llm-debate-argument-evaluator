"""
Tree dependency injection module - Registers tree-related services.
"""

from features.tree.tree_metadata_repository import TreeMetadataRepository
from features.tree.multi_tree_state_service import MultiTreeStateService
from features.tree.tree_selection_service import TreeSelectionService
from features.tree.traversal_logic import TraversalLogic
from utils.dependency_registry import DependencyRegistry
from utils.logger import logger


class TreeInjector:
    def __init__(self, registry: DependencyRegistry):
        """TODO: Add Simple Docstring"""
        self.registry = registry

    def inject(self):
        """Inject tree-related services into the dependency registry."""
        logger.debug("Injecting tree services")

        # Get required dependencies
        repository = self.registry.get("tree_repository")
        supabase_service = self.registry.get("supabase_service")

        # Register tree metadata repository
        tree_metadata_repo = TreeMetadataRepository(supabase_service)
        self.registry.register("tree_metadata_repository", tree_metadata_repo)

        # Register multi-tree state service
        multi_tree_state_service = MultiTreeStateService(repository, tree_metadata_repo)
        self.registry.register("multi_tree_state_service", multi_tree_state_service)

        # Register tree selection service
        tree_selection_service = TreeSelectionService(multi_tree_state_service)
        self.registry.register("tree_selection_service", tree_selection_service)

        # Register traversal logic
        traversal_logic = TraversalLogic(data_service=multi_tree_state_service)
        self.registry.register("traversal_logic", traversal_logic)

        logger.info("Tree services injected successfully")
