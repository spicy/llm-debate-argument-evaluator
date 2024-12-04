import asyncio
import math
from typing import Any, Dict

import networkx as nx
import pygame as pg

from config.visualization_config import visualization_config
from utils.logger import logger
from visualization.observer import Observer


class TreeRenderer(Observer):
    def __init__(self, debate_tree_subject):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)

        # Initialize Pygame
        pg.init()
        self.screen = pg.display.set_mode((1200, 800))
        pg.display.set_caption("Debate Tree Visualization")

        # Visual settings
        self.background_color = (240, 240, 240)
        self.node_radius = 20
        self.font = pg.font.Font(None, 24)

        # Camera/view settings
        self.offset_x = 600  # Center of screen
        self.offset_y = 100  # Top padding
        self.zoom = 1.0

        # Tree layout
        self.level_spacing = 150
        self.node_spacing = 100

        # Node positions
        self.positions = {}
        self.graph = nx.DiGraph()

        logger.info("TreeRenderer initialized")

    def update(self, subject):
        self.update_graph(subject.debate_tree)

    def update_graph(self, debate_tree: Dict[str, Any]):
        if not debate_tree:
            return

        self.graph.clear()
        for node_id, node_data in debate_tree.items():
            # Assuming node_data structure: [priority, counter, node_dict]
            node_dict = node_data[2]
            self.graph.add_node(
                node_id,
                argument=node_dict.get("argument", ""),
                evaluation=node_dict.get("evaluation", 0),
                category=node_dict.get("category", ""),
            )

            # Add edge if there's a parent
            parent = node_dict.get("parent")
            if parent is not None and parent != -1:
                self.graph.add_edge(str(parent), node_id)

        # Calculate positions using hierarchical layout
        self.positions = nx.spring_layout(self.graph)

    def get_node_color(self, score: float) -> tuple:
        """Convert score to RGB color (green for high scores, red for low)"""
        r = int(255 * (1 - score))
        g = int(255 * score)
        return (r, g, 0)

    def draw_node(self, pos: tuple, node_id: str, node_data: Dict):
        screen_pos = (
            int(pos[0] * 400 + self.offset_x),
            int(pos[1] * 400 + self.offset_y),
        )

        # Draw node circle
        score = node_data.get("evaluation", 0.5)
        color = self.get_node_color(score)
        pg.draw.circle(self.screen, color, screen_pos, self.node_radius)

        # Draw node ID
        text = self.font.render(str(node_id), True, (0, 0, 0))
        text_rect = text.get_rect(center=screen_pos)
        self.screen.blit(text, text_rect)

    def draw_edge(self, start_pos: tuple, end_pos: tuple):
        start_screen = (
            int(start_pos[0] * 400 + self.offset_x),
            int(start_pos[1] * 400 + self.offset_y),
        )
        end_screen = (
            int(end_pos[0] * 400 + self.offset_x),
            int(end_pos[1] * 400 + self.offset_y),
        )
        pg.draw.line(self.screen, (0, 0, 0), start_screen, end_screen, 2)

    def draw_argument_info(self, node_id: str, node_data: Dict):
        argument = node_data.get("argument", "")
        if argument:
            # Create a surface for the argument text
            max_width = 300
            text_surface = self.font.render(argument[:50] + "...", True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(10, 10))

            # Draw background
            info_surface = pg.Surface((max_width, 100))
            info_surface.fill((255, 255, 255))
            info_surface.blit(text_surface, text_rect)

            self.screen.blit(info_surface, (10, 10))

    async def start(self, quit_event):
        logger.info("Starting tree visualization")
        clock = pg.time.Clock()
        selected_node = None

        while not quit_event.is_set():
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_event.set()

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # Check if clicked on a node
                    mouse_pos = pg.mouse.get_pos()
                    for node_id, pos in self.positions.items():
                        screen_pos = (
                            int(pos[0] * 400 + self.offset_x),
                            int(pos[1] * 400 + self.offset_y),
                        )
                        distance = math.hypot(
                            mouse_pos[0] - screen_pos[0], mouse_pos[1] - screen_pos[1]
                        )
                        if distance < self.node_radius:
                            selected_node = node_id
                            break

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_EQUALS:  # Zoom in
                        self.zoom *= 1.1
                    elif event.key == pg.K_MINUS:  # Zoom out
                        self.zoom /= 1.1
                    # Arrow keys for panning
                    elif event.key == pg.K_LEFT:
                        self.offset_x += 50
                    elif event.key == pg.K_RIGHT:
                        self.offset_x -= 50
                    elif event.key == pg.K_UP:
                        self.offset_y += 50
                    elif event.key == pg.K_DOWN:
                        self.offset_y -= 50

            # Clear screen
            self.screen.fill(self.background_color)

            # Draw edges
            for edge in self.graph.edges():
                self.draw_edge(self.positions[edge[0]], self.positions[edge[1]])

            # Draw nodes
            for node_id in self.graph.nodes():
                self.draw_node(
                    self.positions[node_id], node_id, self.graph.nodes[node_id]
                )

            # Draw selected node info
            if selected_node:
                self.draw_argument_info(selected_node, self.graph.nodes[selected_node])

            pg.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

        pg.quit()
        logger.info("Tree visualization ended")
