from evaluation.model_factory import ModelFactory
from utils.logger import logger


class ModelSelectionService:
    def __init__(self, model_factory: ModelFactory):
        self.model_factory = model_factory
        self.active_models = set()
        logger.info("ModelSelectionService initialized")

    def select_model(self, model_name: str):
        if self.model_factory.model_exists(model_name):
            self.active_models.add(model_name)
            logger.info(f"Model {model_name} selected")
        else:
            logger.error(f"Attempted to select non-existent model: {model_name}")
            raise ValueError(f"Model {model_name} does not exist")

    def deselect_model(self, model_name: str):
        self.active_models.discard(model_name)
        logger.info(f"Model {model_name} deselected")

    def get_active_models(self):
        active_models = {
            model_name: self.model_factory.get_model(model_name)
            for model_name in self.active_models
        }
        logger.debug(f"Active models: {', '.join(active_models.keys())}")
        return active_models
