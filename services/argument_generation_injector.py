from services.argument_generation_service import ArgumentGenerationService
from utils.logger import logger


class ArgumentGenerationInjector:
    @staticmethod
    def inject_argument_generation_services(registry):
        logger.debug("Injecting argument generation services")

        model_factory = registry.get("model_factory")
        argument_generation_service = ArgumentGenerationService(
            model_factory.get_model("ChatGPT")
        )

        registry.register("argument_generation_service", argument_generation_service)

        logger.info("Argument generation services injected successfully")
