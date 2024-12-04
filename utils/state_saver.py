import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from utils.logger import logger


class StateSaver:
    def __init__(self, save_dir: str = "debug_states"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

    def save_node_state(self, state: Dict[str, Any], prefix: str = "node_state"):
        """Save the current state of nodes to a JSON file with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = self.save_dir / filename

        try:
            # Convert any non-serializable objects to strings
            serializable_state = self._make_serializable(state)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(serializable_state, f, indent=2)
            logger.info(f"Node state saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save node state: {str(e)}")

    def _make_serializable(self, obj: Any) -> Any:
        """Convert non-serializable objects to serializable format"""
        if isinstance(obj, dict):
            return {str(k): self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
