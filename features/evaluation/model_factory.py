"""
TODO: This module...
"""

from typing import Any, Dict

from config.environment import environment_config
from utils.logger import log_execution_time, logger


class ModelFactory:
    def __init__(self):
        """TODO: Add Simple Docstring"""
        self.models: Dict[str, Any] = {}
        logger.debug("ModelFactory initialized")

    def register_model(self, name: str, model: Any):
        """TODO: Add Simple Docstring"""
        if name.upper() not in environment_config.ENABLED_LLMS:
            logger.info(
                f"Model '{name}' is not in ENABLED_LLMS, skipping registration."
            )
            return

        self.models[name] = model
        logger.debug(f"Registered model: {name}")

    def get_model(self, name: str) -> Any:
        """TODO: Add Simple Docstring"""
        model = self.models.get(name)
        if model:
            logger.debug(f"Retrieved model: {name}")
        else:
            logger.warning(f"Model not found: {name}")
        return model

    @log_execution_time
    def get_models(self) -> Dict[str, Any]:
        logger.debug(f"Retrieving all models: {list(self.models.keys())}")
        return self.models

    def get_default_model(self) -> Any:
        """Get the default model, preferring ChatGPT, then Claude."""
        if "ChatGPT" in self.models:
            return self.models["ChatGPT"]
        if "Claude" in self.models:
            return self.models["Claude"]
        if "Google" in self.models:
            return self.models["Google"]
        if "Grok" in self.models:
            return self.models["Grok"]
        if self.models:
            return next(iter(self.models.values()))
        raise ValueError("No LLM models are enabled or registered.")

    def model_exists(self, name: str) -> bool:
        exists = name in self.models
        logger.debug(f"Checked if model {name} exists: {exists}")
        return exists
