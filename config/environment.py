"""
TODO: This module...
"""

import logging
from typing import List

from pydantic import Field, field_validator
import os
from dotenv import load_dotenv

from config.base_config import BaseConfig
from typing import Optional, Any

logger = logging.getLogger(__name__)


def load_environment_variables():
    load_dotenv()

    # Multiple environment support
    env = os.getenv("ENVIRONMENT", "development")

    if env == "development":
        load_dotenv(".env.development")
    elif env == "staging":
        load_dotenv(".env.staging")
    elif env == "production":
        load_dotenv(".env.production")


load_environment_variables()


def get_env_variable(var_name: str, default: Optional[Any] = None) -> str:
    """
    Fetches an environment variable. Returns the default only if it was explicitly set (not None).
    Raises an error if the variable is not set and no default is provided.
    """
    value = os.getenv(var_name)
    if value is not None:
        return value
    if default is not None:
        return default
    raise ValueError(
        f"Environment variable '{var_name}' not set and no default provided."
    )


class EnvironmentConfig(BaseConfig):
    # LLM Configuration
    ENABLED_LLMS: List[str] = Field(default_factory=lambda: ["CHATGPT"])
    GENERATION_MODEL: str = "CHATGPT"
    MAX_TOKENS: int = 150

    @field_validator("ENABLED_LLMS", mode="before")
    def standardize_llms(cls, v):
        """Standardizes the LLM names."""
        if isinstance(v, str):
            v = [item.strip().upper() for item in v.split(",")]
        elif isinstance(v, list):
            v = [str(item).strip().upper() for item in v]
        return v

    # API Keys and Endpoints
    CHATGPT_API_KEY: Optional[str] = None
    CHATGPT_API_ENDPOINT: str = "https://api.openai.com/v1/chat/completions"
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_API_ENDPOINT: str = "https://api.anthropic.com/v1/messages"
    GOOGLE_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None

    # Debug and Logging
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    def __init__(self, **data):
        """TODO: Add Simple Docstring"""
        super().__init__(**data)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


environment_config = EnvironmentConfig()
