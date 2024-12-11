from dataclasses import dataclass


@dataclass
class LayoutConfig:
    """Settings for graph layout calculations"""

    vertical_scale: float = 1
    vertical_range: float = 1
    horizontal_space_usage: float = 0.7  # Use 70% of horizontal space
    screen_space_usage: float = 0.7  # Use 70% of available width/height


layout_config = LayoutConfig()
