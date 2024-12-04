import importlib
from typing import Any, Dict

from config.environment import environment_config
from utils.logger import logger


class ModelInjector:
    @staticmethod
    def inject_models(model_factory: Any) -> None:
        logger.debug("Starting model injection")
        logger.debug(f"ENABLED_LLMS: {environment_config.ENABLED_LLMS}")

        models: Dict[str, str] = {}

        if environment_config.CHATGPT_ENABLED:
            models["ChatGPT"] = "evaluation.models.chatgpt_model.ChatGPTModel"
            logger.debug("Added ChatGPT to models list")

        if environment_config.CLAUDE_ENABLED:
            models["Claude"] = "evaluation.models.claude_model.ClaudeModel"
            logger.debug("Added Claude to models list")

        logger.debug(f"Models to be injected: {list(models.keys())}")

        for name, model_path in models.items():
            try:
                module_name, class_name = model_path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                model_class = getattr(module, class_name)
                model_instance = model_class()
                model_factory.register_model(name, model_instance)
                logger.debug(f"Successfully injected {name} model")
            except Exception as e:
                logger.error(f"Failed to inject {name} model: {str(e)}")

        logger.debug(
            f"Available models after injection: {list(model_factory.get_models().keys())}"
        )
