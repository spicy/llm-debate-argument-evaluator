import os
from typing import Union

from dotenv import load_dotenv

load_dotenv()


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
    API_KEY = get_env_variable("API_KEY", "")
    DEBUG_MODE = get_env_variable("DEBUG_MODE", False)
    MAX_TOKENS = get_env_variable("MAX_TOKENS", 150)
    SIMILARITY_THRESHOLD = get_env_variable("SIMILARITY_THRESHOLD", 0.95)


environment_config = EnvironmentConfig()
