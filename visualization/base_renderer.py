"""
TODO: This module...
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseRenderer(ABC):
    """Abstract base class for rendering the tree."""

    @abstractmethod
    def render(self, tree: List[Dict[str, Any]]) -> None:
        """Render the entire tree."""
        pass

    @abstractmethod
    def highlight_path(self, path: List[Dict[str, Any]]) -> None:
        """Highlight the optimal path in the rendered tree."""
        pass
