from commands.evaluate_arguments_command import EvaluateArgumentsCommand
from commands.expand_node_command import ExpandNodeCommand
from commands.generate_arguments_command import GenerateArgumentsCommand
from commands.submit_argument_command import SubmitArgumentCommand
from utils.logger import logger


class CommandInjector:
    @staticmethod
    def inject_commands(registry):
        logger.debug("Injecting commands")

        priority_queue_service = registry.get("priority_queue_service")
        evaluation_service = registry.get("evaluation_service")
        argument_generation_service = registry.get("argument_generation_service")
        score_aggregator_service = registry.get("score_aggregator_service")

        registry.register(
            "expand_node_command",
            ExpandNodeCommand(
                argument_generation_service, evaluation_service, priority_queue_service
            ),
        )
        registry.register(
            "submit_argument_command",
            SubmitArgumentCommand(evaluation_service, priority_queue_service),
        )
        registry.register(
            "generate_arguments_command",
            GenerateArgumentsCommand(
                argument_generation_service, evaluation_service, priority_queue_service
            ),
        )
        registry.register(
            "evaluate_arguments_command",
            EvaluateArgumentsCommand(evaluation_service, score_aggregator_service),
        )

        logger.info("Commands injected successfully")
