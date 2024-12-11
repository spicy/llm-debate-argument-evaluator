from dataclasses import dataclass


@dataclass
class NodeVisualConfig:
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


node_visual_config = NodeVisualConfig()
