"""
TODO: This module...
"""

from typing import Union
from visualization.base_renderer import BaseRenderer
from visualization.pygame_renderer import PygameRenderer
from visualization.plotly_renderer import PlotlyRenderer
from utils.logger import logger


class RendererFactory:
    """Factory for creating different types of renderers"""

    RENDERER_TYPES = {
        "pygame": PygameRenderer,
        "plotly": PlotlyRenderer,
    }

    @classmethod
    def create_renderer(
        cls, renderer_type: str, tree_subject, **kwargs
    ) -> Union[PygameRenderer, PlotlyRenderer, None]:
        """Create a renderer of the specified type"""

        renderer_class = cls.RENDERER_TYPES.get(renderer_type)
        if not renderer_class:
            logger.error(f"Unknown renderer type: {renderer_type}")
            logger.info(f"Available types: {list(cls.RENDERER_TYPES.keys())}")
            return None

        try:
            return renderer_class(tree_subject, **kwargs)
        except ImportError as e:
            logger.error(
                f"Failed to import dependencies for {renderer_type} renderer: {e}"
            )
            logger.info("Make sure you have the required dependencies installed.")
            return None
        except Exception as e:
            logger.error(
                f"Failed to create {renderer_type} renderer: {e}", exc_info=True
            )
            return None


def get_renderer_info():
    """Get information about available renderers and their dependencies"""
    return {
        "pygame": {
            "description": "Original SDL-based renderer with real-time interaction",
            "dependencies": ["pygame", "networkx"],
            "pros": ["Real-time updates", "Interactive controls", "Fast rendering"],
            "cons": ["Basic graphics", "Limited layout options"],
        },
        "plotly": {
            "description": "Interactive Python-based charts with web export",
            "dependencies": ["plotly", "networkx"],
            "pros": ["Interactive", "Easy Python integration", "Export options"],
            "cons": ["Can be slow with large graphs", "Requires browser"],
        },
    }
