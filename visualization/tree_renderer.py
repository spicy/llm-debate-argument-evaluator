import asyncio
import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import networkx as nx
import pygame as pg
from pygame import Surface

from utils.logger import logger
from visualization.observer import Observer


@dataclass
class NodeVisualProperties:
    """Visual properties for rendering nodes"""

    radius: int = 20  # Reduced from 30 to show more nodes
    padding: int = 50  # Reduced from 100 to use more screen space
    font_size: int = 24  # Reduced from 32 for smaller text
    small_font_size: int = 16  # Reduced from 24 for smaller text


@dataclass
class CameraSettings:
    """Camera/view settings for the visualization"""

    offset_x: float
    offset_y: float
    zoom: float = 0.7  # Reduced from 1.0 for initial zoomed out view


class TreeRenderer(Observer):
    """Renders a visual representation of the debate tree using Pygame"""

    def __init__(self, debate_tree_subject, window_size: Tuple[int, int] = (1200, 800)):
        """Initialize the tree renderer with the given debate tree subject"""
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)

        # Initialize visualization components
        self._init_pygame(window_size)
        self._init_visual_properties()

        # Initialize graph components
        self.positions = {}
        self.graph = nx.DiGraph()

        logger.info("TreeRenderer initialized")

    def _init_pygame(self, window_size: Tuple[int, int]) -> None:
        """Initialize Pygame with the given window size"""
        try:
            pg.init()
            self.screen = pg.display.set_mode(window_size)
            pg.display.set_caption("Debate Tree Visualization")
        except pg.error as e:
            logger.error(f"Failed to initialize Pygame: {e}")
            raise

    def _init_visual_properties(self) -> None:
        """Initialize visual properties and settings"""
        self.visual_props = NodeVisualProperties()
        self.camera = CameraSettings(
            offset_x=self.screen.get_width() / 2, offset_y=self.screen.get_height() / 2
        )
        self.background_color = (240, 240, 240)
        self.font = pg.font.Font(None, self.visual_props.font_size)
        self.small_font = pg.font.Font(None, self.visual_props.small_font_size)

    def update(self, subject) -> None:
        """Update the graph when the debate tree changes"""
        self.update_graph(subject.debate_tree)

    def update_graph(self, debate_tree: Dict[str, Any]) -> None:
        """Update the graph structure and calculate node positions"""
        if not debate_tree:
            return

        self._build_graph(debate_tree)
        self._calculate_layout()

    def _build_graph(self, debate_tree: Dict[str, Any]) -> None:
        """Build the NetworkX graph from the debate tree"""
        self.graph.clear()
        for node_id, node_data in debate_tree.items():
            # Node data is now the complete node dictionary
            self._add_node_to_graph(node_id, node_data[-1])

    def _add_node_to_graph(self, node_id: str, node_dict: Dict[str, Any]) -> None:
        """Add a node and its edges to the graph"""
        self.graph.add_node(
            node_id,
            argument=node_dict.get("argument", ""),
            evaluation=node_dict.get("evaluation", 0),
            category=node_dict.get("category", ""),
        )

        parent = node_dict.get("parent")
        if parent is not None and parent != -1:
            self.graph.add_edge(str(parent), node_id)

    def _calculate_layout(self) -> None:
        """Calculate the layout positions for all nodes"""
        if not self.graph.nodes():
            return

        # Calculate initial positions with more spread
        self.positions = nx.spring_layout(
            self.graph, k=3, iterations=50
        )  # Increased k from 2 to 3

        # Scale positions to fit screen
        self._scale_positions_to_screen()

    def _scale_positions_to_screen(self) -> None:
        """Scale node positions to fit within the screen bounds"""
        if not self.positions:
            return

        bounds = self._get_position_bounds()
        available_space = self._get_available_space()

        for node in self.positions:
            self.positions[node] = self._calculate_screen_position(
                self.positions[node], bounds, available_space
            )

    def _get_position_bounds(self) -> Tuple[float, float, float, float]:
        """Get the bounds of all node positions"""
        positions = list(self.positions.values())
        min_x = min(pos[0] for pos in positions)
        max_x = max(pos[0] for pos in positions)
        min_y = min(pos[1] for pos in positions)
        max_y = max(pos[1] for pos in positions)
        return min_x, max_x, min_y, max_y

    def _get_available_space(self) -> Tuple[float, float]:
        """Calculate available space for rendering"""
        padding = self.visual_props.padding
        return (
            self.screen.get_width() - 2 * padding,
            self.screen.get_height() - 2 * padding,
        )

    def _calculate_screen_position(
        self,
        pos: Tuple[float, float],
        bounds: Tuple[float, float, float, float],
        available_space: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Calculate the screen position for a node"""
        min_x, max_x, min_y, max_y = bounds
        available_width, available_height = available_space

        x_norm = (pos[0] - min_x) / (max_x - min_x) if max_x != min_x else 0
        y_norm = (pos[1] - min_y) / (max_y - min_y) if max_y != min_y else 0

        x_screen = (x_norm * available_width) - (available_width / 2)
        y_screen = (y_norm * available_height) - (available_height / 2)

        return (x_screen, y_screen)

    def draw_node(
        self, pos: Tuple[float, float], node_id: str, node_data: Dict
    ) -> None:
        """Draw a node and its labels"""
        screen_pos = self._get_screen_coordinates(pos)

        # Draw node circle
        self._draw_node_circle(screen_pos, node_data.get("evaluation", 0.5))

        # Draw labels
        self._draw_node_labels(screen_pos, node_id, node_data.get("category", ""))

    def _get_screen_coordinates(self, pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert graph coordinates to screen coordinates"""
        return (int(pos[0] + self.camera.offset_x), int(pos[1] + self.camera.offset_y))

    def _draw_node_circle(self, screen_pos: Tuple[int, int], evaluation: float) -> None:
        """Draw the node circle with evaluation-based color"""
        color = self._get_node_color(evaluation)
        pg.draw.circle(self.screen, color, screen_pos, self.visual_props.radius)
        pg.draw.circle(self.screen, (0, 0, 0), screen_pos, self.visual_props.radius, 2)

    def _get_node_color(self, score: float) -> Tuple[int, int, int]:
        """Convert evaluation score to RGB color"""
        r = int(255 * (1 - score))
        g = int(255 * score)
        return (r, g, 0)

    def _draw_node_labels(
        self, screen_pos: Tuple[int, int], node_id: str, category: str
    ) -> None:
        """Draw node ID and category labels"""
        if category:
            self._draw_text(
                category,
                self.small_font,
                (0, 0, 0),
                (
                    screen_pos[0],
                    screen_pos[1] - self.visual_props.radius - 10,
                ),  # Reduced spacing from 15 to 10
            )

        self._draw_text(str(node_id), self.small_font, (0, 0, 0), screen_pos)

    def _draw_text(
        self,
        text: str,
        font: pg.font.Font,
        color: Tuple[int, int, int],
        position: Tuple[int, int],
    ) -> None:
        """Draw text centered at the given position"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        self.screen.blit(text_surface, text_rect)

    async def start(self, quit_event) -> None:
        """Start the visualization loop"""
        logger.info("Starting tree visualization")
        try:
            await self._run_visualization_loop(quit_event)
        finally:
            pg.quit()
            logger.info("Tree visualization ended")

    async def _run_visualization_loop(self, quit_event) -> None:
        """Main visualization loop"""
        clock = pg.time.Clock()
        selected_node = None

        while not quit_event.is_set():
            selected_node = self._handle_events(quit_event, selected_node)
            self._render_frame(selected_node)
            clock.tick(60)
            await asyncio.sleep(0)

        pg.quit()

    def _handle_events(self, quit_event, selected_node: Optional[str]) -> Optional[str]:
        """Handle Pygame events and return updated selected node"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit_event.set()
                return selected_node

            if event.type == pg.MOUSEBUTTONDOWN:
                selected_node = self._handle_mouse_click(event.pos)
            elif event.type == pg.KEYDOWN:
                self._handle_keyboard_input(event.key)

        return selected_node

    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click and return clicked node ID if any"""
        for node_id, pos in self.positions.items():
            screen_pos = self._get_screen_coordinates(pos)
            distance = math.hypot(
                mouse_pos[0] - screen_pos[0], mouse_pos[1] - screen_pos[1]
            )
            if distance < self.visual_props.radius:
                return node_id
        return None

    def _handle_keyboard_input(self, key: int) -> None:
        """Handle keyboard input for camera controls"""
        if key == pg.K_EQUALS:
            self.camera.zoom *= 1.1
        elif key == pg.K_MINUS:
            self.camera.zoom /= 1.1
        elif key == pg.K_LEFT:
            self.camera.offset_x += 50
        elif key == pg.K_RIGHT:
            self.camera.offset_x -= 50
        elif key == pg.K_UP:
            self.camera.offset_y += 50
        elif key == pg.K_DOWN:
            self.camera.offset_y -= 50

    def _render_frame(self, selected_node: Optional[str]) -> None:
        """Render a single frame of the visualization"""
        self.screen.fill(self.background_color)
        self._draw_edges()
        self._draw_nodes()

        if selected_node:
            self._draw_selected_node_info(selected_node)

        pg.display.flip()

    def _draw_edges(self) -> None:
        """Draw all edges in the graph"""
        for edge in self.graph.edges():
            if edge[0] in self.positions and edge[1] in self.positions:
                start_pos = self._get_screen_coordinates(self.positions[edge[0]])
                end_pos = self._get_screen_coordinates(self.positions[edge[1]])
                pg.draw.line(self.screen, (0, 0, 0), start_pos, end_pos, 2)

    def _draw_nodes(self) -> None:
        """Draw all nodes in the graph"""
        for node_id in self.graph.nodes():
            if node_id in self.positions:
                self.draw_node(
                    self.positions[node_id], node_id, self.graph.nodes[node_id]
                )

    def _draw_selected_node_info(self, node_id: str) -> None:
        """Draw information for the selected node"""
        node_data = self.graph.nodes[node_id]
        argument = node_data.get("argument", "")
        if argument:
            self._draw_argument_info(argument)

    def _draw_argument_info(self, argument: str) -> None:
        """Draw argument information panel"""
        max_width = 300
        text_surface = self.font.render(argument[:50] + "...", True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=(10, 10))

        info_surface = Surface((max_width, 100))
        info_surface.fill((255, 255, 255))
        info_surface.blit(text_surface, text_rect)

        self.screen.blit(info_surface, (10, 10))
