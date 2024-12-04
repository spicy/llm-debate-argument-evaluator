from typing import Any, Dict

from utils.logger import log_execution_time, logger


class ModelFactory:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        logger.debug("ModelFactory initialized")

    def register_model(self, name: str, model: Any):
        self.models[name] = model
        logger.debug(f"Registered model: {name}")

    def get_model(self, name: str) -> Any:
        model = self.models.get(name)
        if model:
            logger.debug(f"Retrieved model: {name}")
        else:
            logger.warning(f"Model not found: {name}")
        return model

    @log_execution_time
    def get_models(self) -> Dict[str, Any]:
        logger.debug("Retrieving all models")
        return self.models

    def model_exists(self, name: str) -> bool:
        exists = name in self.models
        logger.debug(f"Checked if model {name} exists: {exists}")
        return exists
