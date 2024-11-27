from typing import Any, Dict

import aiohttp
from aiohttp import ClientError

from config.environment import get_env_variable
from utils.logger import log_execution_time, logger

from .base_api_client import BaseAPIClient


class ClaudeAPIClient(BaseAPIClient):
    def __init__(self):
        self.api_key = get_env_variable("CLAUDE_API_KEY")
        self.api_endpoint = get_env_variable("CLAUDE_API_ENDPOINT")
        self.model = "claude-3-5-sonnet-20241022"
        logger.info("ClaudeAPIClient initialized")

    @log_execution_time
    async def evaluate(self, system_message: str, prompt: str, max_tokens: int = 20) -> float:
        logger.info(f"Evaluating prompt: {prompt[:50]}...")
        headers = self._get_headers()
        data = self._prepare_request_data(prompt, system_message=system_message, max_tokens=max_tokens)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint, headers=headers, json=data
                ) as response:
                    await self._check_response(response)

                    result = await response.json()
                    score = self._extract_score(result)
                    logger.info(f"Evaluation completed. Score: {score}")
                    return score
        except ClientError as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        finally:
            await session.close()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": f"{self.api_key}",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _prepare_request_data(self, prompt: str, system_message: str = None, max_tokens: int = 0) -> Dict[str, Any]:
        return {
            "model": self.model,
            "system": system_message,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
        }

    async def _check_response(self, response: aiohttp.ClientResponse) -> None:
        if response.status != 200:
            error_detail = await response.text()
            logger.error(
                f"API request failed with status {response.status}: {error_detail}"
            )
            raise Exception(
                f"API request failed with status {response.status}: {error_detail}"
            )

    def _extract_score(self, result: Dict[str, Any]) -> float:
        try:
            content = result["content"][0]["text"]
            # Assuming the content is a string representation of a float
            return float(content)
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to extract score from API response: {str(e)}")
            raise Exception(f"Failed to extract score from API response: {str(e)}")
