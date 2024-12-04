from config.environment import environment_config
from services.argument_generation_service import ArgumentGenerationService
from utils.logger import logger


class ArgumentGenerationInjector:
    @staticmethod
    def inject_argument_generation_services(registry):
        logger.debug("Injecting argument generation services")

        model_factory = registry.get("model_factory")

        # Try to get ChatGPT first, fall back to any available model
        model = None
        if environment_config.CHATGPT_ENABLED:
            model = model_factory.get_model("ChatGPT")
        if not model and environment_config.CLAUDE_ENABLED:
            model = model_factory.get_model("Claude")

        if not model:
            raise ValueError(
                "No LLM models are enabled. Please enable at least one model in your environment configuration."
            )

        argument_generation_service = ArgumentGenerationService(model)
        registry.register("argument_generation_service", argument_generation_service)

        logger.info(
            f"Argument generation services injected successfully using {model.__class__.__name__}"
        )
