"""
TODO: This module...
"""

import re
from typing import Any, Dict

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from config.environment import get_env_variable
from utils.logger import log_execution_time, logger

from .base_api_client import BaseAPIClient


class GoogleAPIClient(BaseAPIClient):
    def __init__(self):
        self.api_key = get_env_variable("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = get_env_variable("GOOGLE_MODEL_NAME")
        logger.info("GoogleAPIClient initialized")

    @log_execution_time
    async def evaluate(
        self, system_message: str, prompt: str, max_tokens: int = 100
    ) -> float:
        logger.info(f"Evaluating prompt: {prompt[:50]}...")
        try:
            model = genai.GenerativeModel(self.model)
            full_prompt = f"{system_message}\n{prompt}"
            response = await model.generate_content_async(full_prompt)
            score = self._extract_score(response.text)
            logger.info(f"Evaluation completed. Score: {score}")
            return score
        except google_exceptions.PermissionDenied as e:
            logger.error(f"API Permission Denied: {e}")
            raise ConnectionRefusedError(f"API Permission Denied: {e}") from e
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"API Resource Exhausted: {e}")
            raise ConnectionAbortedError(f"API Resource Exhausted: {e}") from e
        except google_exceptions.GoogleAPICallError as e:
            logger.error(f"API call failed: {e}")
            raise ConnectionError(f"API call failed: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            raise

    async def generate_text(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int = 150,
    ) -> str:
        logger.info(f"Generating text for prompt: {prompt[:50]}...")
        try:
            model = genai.GenerativeModel(self.model)
            full_prompt = f"{system_message}\n{prompt}"
            response = await model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens
                ),
            )
            logger.info("Text generation completed")
            return response.text
        except google_exceptions.PermissionDenied as e:
            logger.error(f"API Permission Denied: {e}")
            raise ConnectionRefusedError(f"API Permission Denied: {e}") from e
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"API Resource Exhausted: {e}")
            raise ConnectionAbortedError(f"API Resource Exhausted: {e}") from e
        except google_exceptions.GoogleAPICallError as e:
            logger.error(f"API call failed: {e}")
            raise ConnectionError(f"API call failed: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            raise

    def _get_headers(self) -> Dict[str, str]:
        # Not needed for the google-generativeai library
        return {}

    def _prepare_request_data(
        self, prompt: str, system_message: str = None, max_tokens: int = 0
    ) -> Dict[str, Any]:
        """TODO: Add Simple Docstring"""
        # TODO: REFACTOR for liskov substitution principle
        return {}

    async def _check_response(self, response: Any) -> None:
        """TODO: Add Simple Docstring"""
        # TODO: REFACTOR for liskov substitution principle
        # The library handles response checking and raises exceptions.
        pass

    def _extract_score(self, content: str) -> float:
        """TODO: Add Simple Docstring"""
        try:
            # Look for "SCORE: X.XX" pattern
            score_match = re.search(r"SCORE:\s*(\d+\.?\d*)", content, re.IGNORECASE)
            if score_match:
                return float(score_match.group(1))
            raise ValueError(
                f"No properly formatted score found in response: {content}"
            )
        except Exception as e:
            logger.error(f"Failed to extract score from API response: {str(e)}")
            raise Exception(f"Failed to extract score from API response: {str(e)}")
