"""
TODO: This module...
"""

from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
from features.tree.tree_repository import TreeRepository
from utils.logger import logger

try:
    import pygame as pg
    from pygame import Surface

    PYGAME_AVAILABLE = True
except ImportError:
    pg = None
    Surface = None
    PYGAME_AVAILABLE = False


class NodeScoreDisplay:
    """Displays node scores using a color-coded legend."""

    def __init__(self, repository: TreeRepository):
        """TODO: Add Simple Docstring"""
        self.repository = repository
        self.fig, self.ax = plt.subplots(figsize=(6, 1))
        self.fig.subplots_adjust(bottom=0.5)

    def display_scores(self) -> None:
        """TODO: Add Simple Docstring"""
        logger.info("Displaying node scores")
        nodes = self.repository.get_all_nodes()
        if not nodes:
            logger.info("No nodes to display.")
            return

        for node in sorted(nodes, key=lambda x: x.get("id", 0)):
            # Skip root nodes from score display as they represent topics, not arguments
            if node.get("argument_type") == "root":
                logger.info(
                    f"Node {node.get('id', 'N/A')}: Root node (topic: {node.get('argument', 'Unknown')})"
                )
                continue

            score = node.get("evaluation", {}).get("average", 0)
            color = self._get_color_for_score(score)
            logger.info(
                f"Node {node.get('id', 'N/A')}: Score = {score:.2f}, Color = {color}"
            )

    def _get_color_for_score(self, score: float) -> str:
        """Interpolates color from red to green based on score."""
        # Clamping score between 0 and 1
        score = max(0, min(1, score))
        # RGB interpolation: from red (1,0,0) to green (0,1,0)
        r = 1 - score
        g = score
        b = 0
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def draw_selected_node_details(
        self, surface: Surface, selected_node_id: str, node_data: Optional[Dict] = None
    ) -> None:
        """Draw a detailed info panel for the selected node."""
        if not PYGAME_AVAILABLE or not surface or not selected_node_id:
            return

        try:
            from config.node_visual_config import node_visual_config

            # Use provided node data or fall back to repository lookup
            if node_data:
                selected_node = node_data
            else:
                # Fallback: Get node data from repository
                nodes = self.repository.get_all_nodes()
                selected_node = None

                for node in nodes:
                    if str(node.get("id")) == str(selected_node_id):
                        selected_node = node
                        break

                if not selected_node:
                    logger.warning(
                        f"Selected node {selected_node_id} not found in repository"
                    )
                    return

            # Extract node information
            node_id = selected_node.get("id", "Unknown")
            argument = selected_node.get("argument", "No argument available")
            evaluation = selected_node.get("evaluation", {})
            if isinstance(evaluation, dict):
                score = evaluation.get("average", 0.0)
            else:
                score = float(evaluation) if evaluation else 0.0

            arg_type = selected_node.get("argument_type", "unknown")
            visits = selected_node.get("visits", 0)
            wins = selected_node.get("wins", 0.0)
            win_rate = (wins / visits) if visits > 0 else 0.0

            # Screen constraints
            screen_width = surface.get_width()
            screen_height = surface.get_height()
            panel_padding = node_visual_config.node_info_panel_padding

            # Font setup
            font = pg.font.Font(None, 20)
            title_font = pg.font.Font(None, 24)

            # Calculate responsive panel width
            min_panel_width = 300  # Minimum readable width
            max_panel_width = min(600, screen_width // 2)  # Max 50% of screen or 600px
            preferred_panel_width = node_visual_config.node_info_panel_width

            # Analyze text to determine optimal width
            title_text = f"Node {node_id} Details"
            title_width = title_font.size(title_text)[0] + (panel_padding * 2)

            # Calculate width needed for stats lines
            stats_lines = [
                f"Type: {arg_type.upper()}",
                f"Score: {score:.3f}" if arg_type != "root" else "",
                f"Visits: {visits}" if arg_type != "root" else "",
                f"Win Rate: {win_rate:.2f}" if arg_type != "root" else "",
            ]
            max_stats_width = max(
                [font.size(line)[0] for line in stats_lines if line]
            ) + (panel_padding * 2)

            # Calculate optimal width for argument text
            words = argument.split()
            if words:
                # Try different widths to find optimal line breaks
                test_widths = [min_panel_width, preferred_panel_width, max_panel_width]
                best_width = min_panel_width
                best_line_count = float("inf")

                for test_width in test_widths:
                    if test_width > max_panel_width:
                        continue

                    max_line_width = test_width - (panel_padding * 2)
                    test_lines = []
                    current_line = ""

                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        text_width = font.size(test_line)[0]
                        if text_width <= max_line_width:
                            current_line = test_line
                        else:
                            if current_line:
                                test_lines.append(current_line)
                            current_line = word
                    if current_line:
                        test_lines.append(current_line)

                    # Prefer width that gives reasonable line count
                    if len(test_lines) < best_line_count and len(test_lines) <= 20:
                        best_line_count = len(test_lines)
                        best_width = test_width

                panel_width = max(best_width, title_width, max_stats_width)
                panel_width = min(panel_width, max_panel_width)
            else:
                panel_width = max(min_panel_width, title_width, max_stats_width)

            # Now wrap text with the determined optimal width
            max_line_width = panel_width - (panel_padding * 2)
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                text_width = font.size(test_line)[0]
                if text_width <= max_line_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Limit to reasonable number of lines based on screen height
            max_lines = min(20, (screen_height - 200) // 22)  # Leave space for UI
            if len(lines) > max_lines:
                lines = lines[: max_lines - 1] + ["..."]

            # Calculate panel height based on actual content
            line_height = 22
            title_height = 30
            stats_line_count = len([line for line in stats_lines if line])
            stats_height = (
                stats_line_count * line_height
            ) + 40  # 40px for spacing and separator
            argument_header_height = 30  # "Argument:" header

            panel_height = (
                title_height
                + stats_height
                + argument_header_height
                + (len(lines) * line_height)
                + (panel_padding * 2)
            )

            # Position panel intelligently on screen
            margin = 20

            # Try right side first (preferred)
            panel_x = screen_width - panel_width - margin
            panel_y = margin

            # Adjust if panel doesn't fit
            if panel_x < margin:  # Too wide for screen
                panel_x = margin
                panel_width = screen_width - (margin * 2)
                # Recalculate with new width
                max_line_width = panel_width - (panel_padding * 2)
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    text_width = font.size(test_line)[0]
                    if text_width <= max_line_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                # Recalculate height
                panel_height = (
                    title_height
                    + stats_height
                    + argument_header_height
                    + (len(lines) * line_height)
                    + (panel_padding * 2)
                )

            if panel_y + panel_height > screen_height - margin:
                panel_y = max(margin, screen_height - panel_height - margin)

            # Draw panel background
            panel_rect = pg.Rect(panel_x, panel_y, panel_width, panel_height)
            pg.draw.rect(surface, pg.Color("#2c3e50"), panel_rect)  # Dark background
            pg.draw.rect(surface, pg.Color("#34495e"), panel_rect, 3)  # Border

            # Draw title
            title_text = f"Node {node_id} Details"
            title_surface = title_font.render(title_text, True, pg.Color("#ecf0f1"))
            surface.blit(
                title_surface, (panel_x + panel_padding, panel_y + panel_padding)
            )

            # Draw node statistics using pre-calculated lines
            y_offset = panel_y + panel_padding + title_height

            for i, stats_line in enumerate(stats_lines):
                if not stats_line:  # Skip empty lines
                    continue

                # Special color for score line
                if stats_line.startswith("Score:") and arg_type != "root":
                    color = self._get_score_color_pygame(score)
                else:
                    color = pg.Color("#bdc3c7")

                stats_surface = font.render(stats_line, True, color)
                surface.blit(stats_surface, (panel_x + panel_padding, y_offset))
                y_offset += line_height

            # Draw separator line
            y_offset += 10
            line_start = (panel_x + panel_padding, y_offset)
            line_end = (panel_x + panel_width - panel_padding, y_offset)
            pg.draw.line(surface, pg.Color("#34495e"), line_start, line_end, 2)
            y_offset += 15

            # Draw argument header
            arg_header = "Argument:"
            header_surface = font.render(arg_header, True, pg.Color("#ecf0f1"))
            surface.blit(header_surface, (panel_x + panel_padding, y_offset))
            y_offset += line_height + 5

            # Draw argument text lines
            for line in lines:
                line_surface = font.render(line, True, pg.Color("#bdc3c7"))
                surface.blit(line_surface, (panel_x + panel_padding, y_offset))
                y_offset += line_height

        except Exception as e:
            logger.error(f"Error drawing selected node details: {e}")

    def _get_score_color_pygame(self, score: float) -> pg.Color:
        """Get pygame color for score visualization."""
        if score >= 0.7:
            return pg.Color("#4caf50")  # Green
        elif score >= 0.5:
            return pg.Color("#ffc107")  # Yellow
        else:
            return pg.Color("#f44336")  # Red
