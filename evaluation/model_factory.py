from typing import Any, Dict

from config.environment import environment_config
from utils.logger import log_execution_time, logger


class ModelFactory:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        logger.debug("ModelFactory initialized")

    def register_model(self, name: str, model: Any):
        if name == "Claude" and not environment_config.CLAUDE_ENABLED:
            logger.info("Claude model disabled, skipping registration")
            return
        if name == "ChatGPT" and not environment_config.CHATGPT_ENABLED:
            logger.info("ChatGPT model disabled, skipping registration")
            return

        self.models[name] = model
        logger.debug(f"Registered model: {name}")

    def get_model(self, name: str) -> Any:
        if name not in self.models:
            available_models = list(self.models.keys())
            if not available_models:
                raise ValueError(
                    "No LLM models are enabled. Please enable at least one model in your environment configuration."
                )
            # Return the first available model if requested model isn't available
            name = available_models[0]
            logger.warning(
                f"Requested model {name} not available. Using {name} instead."
            )

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

    def model_exists(self, name: str) -> bool:
        exists = name in self.models
        logger.debug(f"Checked if model {name} exists: {exists}")
        return exists
