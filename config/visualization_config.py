"""
TODO: This module...
"""

from typing import Dict, Optional

from config.base_config import BaseConfig


class VisualizationConfig(BaseConfig):
    # Set to None to prompt user, or specify: "pygame", "web", "plotly"
    RENDERER_TYPE: Optional[str] = "pygame"  # Options: "pygame", "web", "plotly", None
    SCREEN_WIDTH: int = 1920
    SCREEN_HEIGHT: int = 1080
    BORDER_WIDTH: int = 4
    BORDER_COLORS: Dict[str, str] = {
        "root": "#4A90E2",  # A nice blue
        "supporting": "#50E3C2",  # A teal/turquoise
        "against": "#F5A623",  # An orange/yellow
    }
    # For Web and Plotly Renderers
    NODE_COLORS: Dict[str, str] = {
        "optimal": "#ff9800",
        "root": "#2196f3",
        "high_score": "#4caf50",
        "medium_score": "#ffc107",
        "low_score": "#f44336",
    }
    EDGE_COLORS: Dict[str, str] = {"default": "#bdc3c7", "optimal": "#9b59b6"}


visualization_config: VisualizationConfig = VisualizationConfig()
