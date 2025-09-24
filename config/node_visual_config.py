"""
TODO: This module...
"""

from config.base_config import BaseConfig


class NodeVisualConfig(BaseConfig):
    """Visual properties for rendering nodes"""

    radius: int = 30
    padding: int = 100
    font_size: int = 24
    small_font_size: int = 16
    node_outline_width: int = 2
    node_label_offset: int = 10
    node_info_panel_width: int = 450
    node_info_text_width: int = 50
    node_info_text_height: int = 20
    node_info_panel_padding: int = 15
    node_info_vertical_offset: int = 50
    node_info_text_vertical_offset: int = 20

    # Colors for pygame renderer
    background_color: str = "#2c3e50"  # Dark blue-gray background
    node_color_optimal: str = "#ff9800"  # Orange for optimal path
    node_color_high: str = "#4caf50"  # Green for high scores
    node_color_medium: str = "#ffc107"  # Yellow for medium scores
    node_color_low: str = "#f44336"  # Red for low scores
    edge_color: str = "#ecf0f1"  # Light gray for regular edges
    edge_color_optimal: str = "#9b59b6"  # Purple for optimal path edges


node_visual_config: NodeVisualConfig = NodeVisualConfig()
