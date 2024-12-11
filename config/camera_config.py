from dataclasses import dataclass


@dataclass
class CameraConfig:
    """Camera/view settings for the visualization"""

    offset_x: float = 0.0
    offset_y: float = 0.0
    zoom: float = 0.9
    pan_step: int = 100
    zoom_factor: float = 1.1


camera_config = CameraConfig()
