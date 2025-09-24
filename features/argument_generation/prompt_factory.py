"""
TODO: This module...
"""

from utils.logger import logger


class PromptFactory:
    @staticmethod
    def create_support_prompt(argument: str, topic: str, subcategory: str) -> str:
        """Create a detailed prompt for generating a supporting argument."""
        prompt = (
            f"In the context of the topic '{topic}' and subcategory '{subcategory}', "
            f"consider the argument: '{argument}'. "
            "Provide a well-reasoned supporting argument that:\n"
            "- Directly reinforces the original statement.\n"
            "- Introduces new evidence or a new line of reasoning.\n"
            "- Avoids simply restating the original argument.\n"
            "- Is concise and to the point."
        )
        logger.debug(f"Generated support prompt for topic '{topic}'")
        return prompt

    @staticmethod
    def create_against_prompt(argument: str, topic: str, subcategory: str) -> str:
        """Create a detailed prompt for generating an opposing argument."""
        prompt = (
            f"In the context of the topic '{topic}' and subcategory '{subcategory}', "
            f"consider the argument: '{argument}'. "
            "Provide a compelling counter-argument that:\n"
            "- Directly challenges the original statement's premise or conclusion.\n"
            "- Introduces conflicting evidence or an alternative perspective.\n"
            "- Identifies any logical fallacies in the original argument, if applicable.\n"
            "- Is respectful and constructive in tone."
        )
        logger.debug(f"Generated against prompt for topic '{topic}'")
        return prompt
