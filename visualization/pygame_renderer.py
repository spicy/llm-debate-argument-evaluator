"""
TODO: This module...
"""

import asyncio
import math
import threading
from textwrap import wrap
from typing import Any, Dict, Optional, Tuple, List

from utils.logger import logger

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
from utils.logger import ensure_logger_in_thread
from visualization.base_renderer import BaseRenderer
from visualization.node_score_display import NodeScoreDisplay
from features.tree.tree_repository import TreeRepository
from utils.color_utils import score_to_gradient_color


class PygameRenderer(BaseRenderer):
    """Renders the tree using Pygame."""

    def __init__(
        self,
        tree_subject: Subject,
        repository: TreeRepository,
        **kwargs,
    ):
        self.tree_subject = tree_subject
        self.repository = repository
        self.config = visualization_config
        self.node_config = node_visual_config
        self.layout_config = layout_config
        self.camera_config = CameraConfig()
        self._is_dirty = True  # Flag to trigger redraw
        self._tree_data = {}
        self._optimal_path_data = None
        self._lock = threading.Lock()

        # Initialize NetworkX graph and other required attributes
        if nx:
            self.graph = nx.DiGraph()
        else:
            logger.error("NetworkX not available - Pygame renderer requires networkx")
            raise ImportError("NetworkX is required for Pygame renderer")

        self.node_positions = {}
        self.selected_node = None
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.drag_offset = (0, 0)

        # Initialize node score display
        self.node_score_display = NodeScoreDisplay(repository)

        # Pygame-specific attributes (will be initialized in start methods)
        self.screen = None
        self.draw_surface = None
        self.font = None
        self.clock = None

        self.tree_subject.add_observer(self)

        logger.info("PygameRenderer dependencies initialized")

    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        world_x, world_y = world_pos
        screen_x = int(
            (world_x + self.camera_config.offset_x) * self.camera_config.zoom
        )
        screen_y = int(
            (world_y + self.camera_config.offset_y) * self.camera_config.zoom
        )
        return (screen_x, screen_y)

    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        screen_x, screen_y = screen_pos
        world_x = (screen_x / self.camera_config.zoom) - self.camera_config.offset_x
        world_y = (screen_y / self.camera_config.zoom) - self.camera_config.offset_y
        return (world_x, world_y)

    def zoom_at(self, screen_pos: Tuple[int, int], zoom_factor: float) -> None:
        """Zoom in/out while keeping the specified screen position fixed."""
        # Convert screen position to world coordinates before zoom
        world_pos = self.screen_to_world(screen_pos)

        # Apply zoom
        self.camera_config.zoom *= zoom_factor

        # Adjust offset to keep the world position under the mouse
        new_screen_pos = self.world_to_screen(world_pos)
        screen_x, screen_y = screen_pos
        new_screen_x, new_screen_y = new_screen_pos

        # Adjust offset to compensate
        self.camera_config.offset_x += (
            screen_x - new_screen_x
        ) / self.camera_config.zoom
        self.camera_config.offset_y += (
            screen_y - new_screen_y
        ) / self.camera_config.zoom

    def pan(self, delta_x: float, delta_y: float) -> None:
        """Pan the camera by the given delta in screen coordinates."""
        self.camera_config.offset_x += delta_x / self.camera_config.zoom
        self.camera_config.offset_y += delta_y / self.camera_config.zoom

    def render(self, tree: List[Dict[str, Any]]) -> None:
        """Render the entire tree."""
        if not tree:
            return
        self.update_graph(tree)
        self._calculate_layout()
        self._draw_tree()

    def highlight_path(self, path: List[Dict[str, Any]]) -> None:
        """Highlight the optimal path in the rendered tree."""
        optimal_path_ids = {str(node["id"]) for node in path}
        self._draw_tree(optimal_path_ids)

    async def update(self, tree: Dict[str, Any], optimal_path: Optional[List] = None):
        """Receives new data and flags the renderer for a redraw."""
        with self._lock:
            self._tree_data = tree
            self._optimal_path_data = optimal_path
            self._is_dirty = True

    def update_graph(self, nodes: List[Dict[str, Any]]):
        """Update the graph from the tree data."""
        self.graph.clear()

        # First pass: Add all nodes
        for node in nodes:
            if node is None:
                logger.warning("Skipping None node in update_graph")
                continue

            node_id = str(node["id"])

            # Ensure node has required fields for visualization
            safe_node = {
                "id": node.get("id"),
                "argument": node.get("argument", "Unknown"),
                "evaluation": node.get("evaluation", {"average": 0}),
                "parent_id": node.get("parent_id"),
                "depth": node.get("depth", 0),
                "argument_type": node.get("argument_type", "unknown"),
                "visits": node.get("visits", 0),
                "wins": node.get("wins", 0.0),
                "category": node.get("category", ""),
                "topic": node.get("topic", ""),
            }

            self.graph.add_node(node_id, **safe_node)

        # Second pass: Add all edges (now that all nodes exist)
        for node in nodes:
            if node is None:
                continue

            node_id = str(node["id"])
            if "parent_id" in node and node["parent_id"] is not None:
                parent_id = str(node["parent_id"])
                if self.graph.has_node(parent_id):
                    self.graph.add_edge(parent_id, node_id)
                else:
                    logger.warning(
                        f"Parent node {parent_id} not found for child {node_id}"
                    )

    def _calculate_layout(self):
        """Calculate node positions using a layout algorithm."""
        if self.graph.number_of_nodes() == 0:
            return

        roots = [n for n, d in self.graph.in_degree() if d == 0]
        if not roots:
            # If no root, try to find a reasonable node to start from
            roots = [next(iter(self.graph.nodes()))]

        try:
            # Check if Graphviz is available
            if not hasattr(nx.drawing, "nx_agraph"):
                raise ImportError("NetworkX Graphviz interface not available")

            # Try to use the more sophisticated Graphviz layout
            pos = nx.drawing.nx_agraph.graphviz_layout(
                self.graph, prog=self.layout_config.prog, root=roots[0]
            )
            logger.info(
                f"Successfully used Graphviz {self.layout_config.prog} layout with {len(pos)} nodes"
            )
        except ImportError as e:
            logger.warning(
                f"Graphviz interface not available ({e}). Install pygraphviz for better layouts: "
                "pip install pygraphviz. Falling back to spring layout."
            )
            pos = nx.spring_layout(self.graph, seed=42)
        except Exception as e:
            logger.warning(
                f"Graphviz layout failed with error: {e}. "
                f"Graph has {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges. "
                f"Root nodes: {roots}. Falling back to spring layout."
            )
            # Fallback to a simpler layout that doesn't require external dependencies
            pos = nx.spring_layout(self.graph, seed=42)

        min_x = min(p[0] for p in pos.values()) if pos else 0
        max_x = max(p[0] for p in pos.values()) if pos else 1
        min_y = min(p[1] for p in pos.values()) if pos else 0
        max_y = max(p[1] for p in pos.values()) if pos else 1

        def scale_pos(p):
            x = (
                (p[0] - min_x) / (max_x - min_x) * (self.screen.get_width() - 100) + 50
                if max_x > min_x
                else self.screen.get_width() / 2
            )
            y = (
                (p[1] - min_y) / (max_y - min_y) * (self.screen.get_height() - 100) + 50
                if max_y > min_y
                else self.screen.get_height() / 2
            )
            return int(x), int(y)

        self.node_positions = {n: scale_pos(p) for n, p in pos.items()}

    def _draw_tree(self, optimal_path_ids: Optional[set] = None):
        """Draw the tree on the screen."""
        self.draw_surface.fill(pg.Color(self.node_config.background_color))

        # Draw edges
        for edge in self.graph.edges():
            start_pos = self.world_to_screen(self.node_positions[edge[0]])
            end_pos = self.world_to_screen(self.node_positions[edge[1]])
            is_optimal = (
                optimal_path_ids
                and edge[0] in optimal_path_ids
                and edge[1] in optimal_path_ids
            )
            color = (
                self.node_config.edge_color_optimal
                if is_optimal
                else self.node_config.edge_color
            )
            pg.draw.line(self.draw_surface, pg.Color(color), start_pos, end_pos, 2)

        # Draw nodes
        for node_id, data in self.graph.nodes(data=True):
            pos = self.world_to_screen(self.node_positions[node_id])
            is_optimal = optimal_path_ids and node_id in optimal_path_ids
            is_selected = node_id == self.selected_node
            self._draw_node(node_id, data, pos, is_optimal, is_selected)

        if self.selected_node and self.graph.has_node(self.selected_node):
            # Get the node data from the graph
            node_data = self.graph.nodes[self.selected_node]
            self.node_score_display.draw_selected_node_details(
                self.draw_surface, self.selected_node, node_data
            )

    def _draw_node(
        self,
        node_id: str,
        data: Dict,
        pos: Tuple[int, int],
        is_optimal: bool,
        is_selected: bool = False,
    ):
        """Draw a single node."""
        # Safety check: handle case where data is None
        if data is None:
            logger.warning(f"Node {node_id} has no data, using defaults")
            data = {
                "evaluation": {"average": 0},
                "argument": "Unknown",
                "visits": 0,
                "wins": 0.0,
            }

        # Extract score safely
        evaluation = data.get("evaluation", {})
        if isinstance(evaluation, dict):
            score = evaluation.get("average", 0)
        else:
            score = float(evaluation) if evaluation else 0

        # Check if this is a root node
        arg_type = data.get("argument_type", "")
        color = self._get_node_color(score, is_optimal, arg_type)
        radius = int(self.node_config.radius * self.camera_config.zoom)
        pg.draw.circle(self.draw_surface, color, pos, radius)

        # Draw selection highlight
        if is_selected:
            highlight_color = pg.Color("#ffffff")  # White highlight
            pg.draw.circle(self.draw_surface, highlight_color, pos, radius + 3, 3)

        # Create multi-line text for node ID and score
        small_font = pg.font.Font(None, self.node_config.small_font_size)

        # Node ID on first line
        id_surface = small_font.render(f"[{node_id}]", True, pg.Color("white"))
        id_rect = id_surface.get_rect()

        # Score on second line
        score_text = f"{score:.2f}" if arg_type != "root" else "ROOT"
        score_surface = small_font.render(score_text, True, pg.Color("white"))
        score_rect = score_surface.get_rect()

        # Position text vertically centered with some offset
        total_height = id_rect.height + score_rect.height
        start_y = pos[1] - total_height // 2

        # Draw ID text
        id_rect.centerx = pos[0]
        id_rect.y = start_y
        self.draw_surface.blit(id_surface, id_rect)

        # Draw score text
        score_rect.centerx = pos[0]
        score_rect.y = start_y + id_rect.height
        self.draw_surface.blit(score_surface, score_rect)

    def _get_node_color(
        self, score: float, is_optimal: bool, arg_type: str = ""
    ) -> pg.Color:
        """Determine node color based on score with gradient from red to green, except for root nodes."""
        # Root nodes are always blue
        if arg_type == "root":
            return pg.Color("#2196f3")  # Blue for root
        return pg.Color(score_to_gradient_color(score))

    def handle_events(self):
        """Handle user input events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            self.handle_mouse_events(event)
        return True

    def handle_mouse_events(self, event):
        """Handle mouse-related events."""
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_node = self._get_node_at_pos(event.pos)
                if clicked_node:
                    # Select the node (this will show the details panel)
                    self.selected_node = clicked_node
                    # Prepare for potential dragging
                    screen_pos = self.world_to_screen(
                        self.node_positions[self.selected_node]
                    )
                    self.drag_offset = (
                        screen_pos[0] - event.pos[0],
                        screen_pos[1] - event.pos[1],
                    )
                else:
                    # Clicked on empty space - deselect node
                    self.selected_node = None
                    self.dragging = False
                    self.last_mouse_pos = event.pos

            elif event.button == 4:  # Zoom in
                self.zoom_at(event.pos, 1.1)
            elif event.button == 5:  # Zoom out
                self.zoom_at(event.pos, 0.9)

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pg.MOUSEMOTION:
            if self.selected_node and pg.mouse.get_pressed()[0]:
                # Check if we should start dragging (mouse moved enough)
                if not self.dragging:
                    # Calculate distance moved since mouse down
                    mouse_down_pos = (
                        event.pos[0] - self.drag_offset[0],
                        event.pos[1] - self.drag_offset[1],
                    )
                    distance = (
                        (event.pos[0] - mouse_down_pos[0]) ** 2
                        + (event.pos[1] - mouse_down_pos[1]) ** 2
                    ) ** 0.5

                    # Start dragging if moved more than threshold
                    if distance > 5:  # 5 pixel threshold
                        self.dragging = True
                # If we're dragging, move the node
                if self.dragging:
                    new_screen_pos = (
                        event.pos[0] + self.drag_offset[0],
                        event.pos[1] + self.drag_offset[1],
                    )
                    self.node_positions[self.selected_node] = self.screen_to_world(
                        new_screen_pos
                    )
            elif not self.dragging and pg.mouse.get_pressed()[0]:
                # Pan the view when not selecting/dragging a node
                self.pan(
                    event.pos[0] - self.last_mouse_pos[0],
                    event.pos[1] - self.last_mouse_pos[1],
                )
                self.last_mouse_pos = event.pos

    def _get_node_at_pos(self, pos: Tuple[int, int]) -> Optional[str]:
        """Get the node ID at a given screen position."""
        for node_id, node_pos_world in self.node_positions.items():
            node_pos_screen = self.world_to_screen(node_pos_world)
            distance = math.hypot(
                pos[0] - node_pos_screen[0], pos[1] - node_pos_screen[1]
            )
            if distance < self.node_config.radius * self.camera_config.zoom:
                return node_id
        return None

    def start_sync(self, quit_event: threading.Event):
        """Start the main loop of the renderer (synchronous version for threading)."""
        # Ensure logger is available in this thread
        thread_logger = ensure_logger_in_thread()
        thread_logger.info("Pygame renderer started in separate thread.")

        try:
            pg.init()
            self.screen = pg.display.set_mode(
                (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pg.RESIZABLE
            )
            self.draw_surface = pg.Surface(
                (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
            )
            pg.display.set_caption("tree Visualization")
            self.font = pg.font.Font(None, self.node_config.font_size)
            self.clock = pg.time.Clock()

            thread_logger.info("Pygame initialized and window created.")

            running = True
            while running and not quit_event.is_set():
                running = self.handle_events()

                # Safely check the dirty flag and get data if needed
                is_dirty_now = False
                local_tree_data = None
                local_optimal_path = None
                with self._lock:
                    if self._is_dirty:
                        is_dirty_now = True
                        local_tree_data = list(self._tree_data.values())
                        local_optimal_path = self._optimal_path_data
                        self._is_dirty = False

                # Rebuild graph only when data has changed
                if is_dirty_now:
                    self.update_graph(local_tree_data)
                    self._calculate_layout()
                    optimal_ids = (
                        {str(node["id"]) for node in local_optimal_path}
                        if local_optimal_path
                        else None
                    )
                    self._draw_tree(optimal_ids)
                elif hasattr(self, "graph") and self.graph.nodes():
                    # Redraw existing tree (for interactive elements like selection)
                    with self._lock:
                        local_optimal_path = self._optimal_path_data
                    optimal_ids = (
                        {str(node["id"]) for node in local_optimal_path}
                        if local_optimal_path
                        else None
                    )
                    self._draw_tree(optimal_ids)

                # Blit the drawing surface to the main screen
                self.screen.blit(self.draw_surface, (0, 0))
                pg.display.flip()

                self.clock.tick(60)  # Control frame rate

        except Exception as e:
            thread_logger.error(f"Error in Pygame renderer: {e}", exc_info=True)
        finally:
            pg.quit()
            thread_logger.info("Pygame renderer stopped.")

    async def start(self, quit_event: asyncio.Event):
        """Start the main loop of the renderer (async version)."""
        logger.info("Starting Pygame renderer in async mode.")

        # Convert asyncio.Event to threading.Event for the sync version
        threading_quit_event = threading.Event()

        def event_bridge():
            while not quit_event.is_set():
                threading_quit_event.wait(0.1)
            threading_quit_event.set()

        # Start the event bridge task
        event_task = asyncio.create_task(asyncio.to_thread(event_bridge))

        try:
            # Run the synchronous renderer in a thread
            await asyncio.to_thread(self.start_sync, threading_quit_event)
        finally:
            threading_quit_event.set()
            await event_task
