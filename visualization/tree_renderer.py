"""
TODO: This module...
"""

import asyncio
import math
import threading
from textwrap import wrap
from typing import Any, Dict, Optional, Tuple, List

try:
    import networkx as nx
    import pygame as pg
    from pygame import Surface
except ImportError:
    # Handle missing optional dependencies
    nx = None
    pg = None
    Surface = None

from config.camera_config import CameraConfig
from config.layout_config import layout_config
from config.node_visual_config import node_visual_config
from config.visualization_config import visualization_config
from utils.subject import Subject
from utils.logger import logger, ensure_logger_in_thread
from visualization.base_renderer import BaseRenderer
from visualization.node_score_display import NodeScoreDisplay
from features.tree.tree_repository import TreeRepository


class TreeRenderer:
    """Manages the rendering of the tree."""

    def __init__(
        self,
        renderer: BaseRenderer,
        repository: TreeRepository,
    ):
        self.renderer = renderer
        self.repository = repository
        logger.info("TreeRenderer initialized")

    def render_and_highlight(self, optimal_path: List[Dict[str, Any]]) -> None:
        """Renders the tree and highlights the optimal path."""
        logger.debug("Rendering tree and highlighting optimal path.")
        all_nodes = self.repository.get_all_nodes()
        if not all_nodes:
            logger.debug("No tree data to render.")
            return

        self.renderer.render(all_nodes)
        if optimal_path:
            self.renderer.highlight_path(optimal_path)

    async def start(self, quit_event: asyncio.Event):
        """Start the renderer."""
        if hasattr(self.renderer, "start"):
            await self.renderer.start(quit_event)
