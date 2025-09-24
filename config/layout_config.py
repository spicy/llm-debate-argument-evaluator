"""
TODO: This module...
"""

from config.base_config import BaseConfig


class LayoutConfig(BaseConfig):
    """Settings for graph layout calculations"""

    vertical_scale: float = 1.0
    vertical_range: float = 1.0
    horizontal_space_usage: float = 0.7  # Use 70% of horizontal space
    screen_space_usage: float = 0.7  # Use 70% of available width/height

    # Graphviz layout program options:
    # - "dot": Hierarchical layouts (best for trees)
    # - "neato": Spring model layouts
    # - "fdp": Force-directed layouts
    # - "sfdp": Large graph force-directed layouts
    # - "twopi": Radial layouts
    # - "circo": Circular layouts
    prog: str = "dot"


layout_config: LayoutConfig = LayoutConfig()
