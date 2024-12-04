from commands.create_root_node_command import CreateRootNodeCommand
from commands.evaluate_debate_tree_command import EvaluateDebateTreeCommand
from commands.expand_node_command import ExpandNodeCommand
from commands.generate_debate_arguments_command import GenerateDebateArgumentsCommand
from commands.load_file_command import LoadFileCommand
from commands.run_debate_tree_command import RunDebateTreeCommand
from commands.submit_argument_command import SubmitArgumentCommand
from commands.traverse_debate_command import TraverseDebateCommand
from utils.logger import logger


class CommandInjector:
    @staticmethod
    def inject_commands(registry):
        logger.debug("Injecting commands")

        # Get services
        priority_queue_service = registry.get("priority_queue_service")
        evaluation_service = registry.get("evaluation_service")
        argument_generation_service = registry.get("argument_generation_service")
        score_aggregator_service = registry.get("score_aggregator_service")

        # Create and register basic commands
        create_root_node_command = CreateRootNodeCommand(priority_queue_service)
        generate_debate_arguments_command = GenerateDebateArgumentsCommand(
            argument_generation_service
        )
        evaluate_debate_tree_command = EvaluateDebateTreeCommand(
            evaluation_service,
            priority_queue_service,
            score_aggregator_service,
        )

        registry.register("create_root_node_command", create_root_node_command)
        registry.register(
            "generate_debate_arguments_command", generate_debate_arguments_command
        )
        registry.register("evaluate_debate_tree_command", evaluate_debate_tree_command)

        # Register dependent commands
        registry.register(
            "expand_node_command",
            ExpandNodeCommand(
                generate_debate_arguments_command,
                evaluation_service,
                priority_queue_service,
                score_aggregator_service,
            ),
        )

        registry.register(
            "submit_argument_command",
            SubmitArgumentCommand(
                evaluation_service,
                priority_queue_service,
                score_aggregator_service,
            ),
        )

        registry.register(
            "load_file_command",
            LoadFileCommand(
                evaluation_service,
                priority_queue_service,
                score_aggregator_service,
            ),
        )

        # Register traverse command last since it depends on other commands
        registry.register(
            "traverse_debate_command",
            TraverseDebateCommand(
                registry.get("traversal_logic"),
                priority_queue_service,
                registry.get("expand_node_command"),
                registry.get("evaluate_debate_tree_command"),
            ),
        )

        # Register the run debate tree command
        registry.register(
            "run_debate_tree_command",
            RunDebateTreeCommand(
                registry.get("create_root_node_command"),
                registry.get("expand_node_command"),
                registry.get("evaluate_debate_tree_command"),
                registry.get("traverse_debate_command"),
            ),
        )

        logger.info("Commands injected successfully")
