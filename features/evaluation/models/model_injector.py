"""
TODO: This module...
"""

import importlib
from typing import Any, Dict

from config.environment import environment_config
from features.evaluation.api_clients import (
    ChatGPTAPIClient,
    ClaudeAPIClient,
    GoogleAPIClient,
    GrokAPIClient,
)
from features.evaluation.models import ChatGPTModel, ClaudeModel, GoogleModel, GrokModel
from utils.logger import logger


class ModelInjector:
    def __init__(self, model_factory):
        """TODO: Add Simple Docstring"""
        self.model_factory = model_factory

    def inject_models(self):
        """TODO: Add Simple Docstring"""
        logger.debug("Starting model injection")
        enabled_llms = [llm.strip().upper() for llm in environment_config.ENABLED_LLMS]
        logger.debug(f"ENABLED_LLMS: {enabled_llms}")

        if "CHATGPT" in enabled_llms:
            self._inject_chatgpt()
        if "CLAUDE" in enabled_llms:
            self._inject_claude()
        if "GOOGLE" in enabled_llms:
            self._inject_google()
        if "GROK" in enabled_llms:
            self._inject_grok()

        logger.debug(
            f"Available models after injection: {self.model_factory.get_models()}"
        )

    def _inject_chatgpt(self):
        """TODO: Add Simple Docstring"""
        api_client = ChatGPTAPIClient()
        model = ChatGPTModel(api_client)
        self.model_factory.register_model("CHATGPT", model)
        logger.debug("Successfully injected ChatGPT model")

    def _inject_claude(self):
        """TODO: Add Simple Docstring"""
        api_client = ClaudeAPIClient()
        model = ClaudeModel(api_client)
        self.model_factory.register_model("CLAUDE", model)
        logger.debug("Successfully injected Claude model")

    def _inject_google(self):
        """TODO: Add Simple Docstring"""
        api_client = GoogleAPIClient()
        model = GoogleModel(api_client)
        self.model_factory.register_model("GOOGLE", model)
        logger.debug("Successfully injected Google model")

    def _inject_grok(self):
        """TODO: Add Simple Docstring"""
        api_client = GrokAPIClient()
        model = GrokModel(api_client)
        self.model_factory.register_model("GROK", model)
        logger.debug("Successfully injected Grok model")
