import importlib
from typing import Any, Dict

from utils.logger import logger


class ModelInjector:
    @staticmethod
    def inject_models(model_factory: Any) -> None:
        logger.debug("Injecting models into ModelFactory")
        models: Dict[str, str] = {
            "ChatGPT": "evaluation.models.chatgpt_model.ChatGPTModel",
            "Claude": "evaluation.models.claude_model.ClaudeModel",
        }

        for name, model_path in models.items():
            module_name, class_name = model_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            model_class = getattr(module, class_name)
            model_instance = model_class()
            model_factory.register_model(name, model_instance)
            logger.debug(f"Injected {name} model")

        logger.debug("Model injection completed")
