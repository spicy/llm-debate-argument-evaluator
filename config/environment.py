import logging
import os
from typing import Union

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_env_variable(
    var_name: str, default: Union[str, int, float, bool] = None
) -> Union[str, int, float, bool]:
    value = os.getenv(var_name)
    if value is None:
        if default is not None:
            return default
        else:
            raise ValueError(f"Environment variable {var_name} is not set")

    # Convert value to appropriate type based on default
    if isinstance(default, bool):
        return value.lower() in ("true", "1", "yes", "on")
    elif isinstance(default, int):
        return int(value)
    elif isinstance(default, float):
        return float(value)
    return value


class EnvironmentConfig:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Debug print
        enabled_llms = get_env_variable("ENABLED_LLMS", "CHATGPT").split(",")
        logger.debug(f"Loaded ENABLED_LLMS from environment: {enabled_llms}")

        self.ENABLED_LLMS = enabled_llms
        self.CHATGPT_ENABLED = "CHATGPT" in self.ENABLED_LLMS
        self.CLAUDE_ENABLED = "CLAUDE" in self.ENABLED_LLMS

        # Debug print
        logger.debug(f"CHATGPT_ENABLED: {self.CHATGPT_ENABLED}")
        logger.debug(f"CLAUDE_ENABLED: {self.CLAUDE_ENABLED}")

        # Other config variables...
        self.API_KEY = get_env_variable("CHATGPT_API_KEY", "")
        self.DEBUG_MODE = get_env_variable("DEBUG_MODE", False)
        self.MAX_TOKENS = get_env_variable("MAX_TOKENS", 150)
        self.SIMILARITY_THRESHOLD = get_env_variable("SIMILARITY_THRESHOLD", 0.95)


environment_config = EnvironmentConfig()
