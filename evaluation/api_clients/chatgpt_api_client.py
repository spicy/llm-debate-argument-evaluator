import re
from typing import Any, Dict

import aiohttp
from aiohttp import ClientError

from config.environment import environment_config, get_env_variable
from utils.logger import log_execution_time, logger

from .base_api_client import BaseAPIClient


class ChatGPTAPIClient(BaseAPIClient):
    def __init__(self):
        self.api_key = get_env_variable("CHATGPT_API_KEY")
        self.api_endpoint = get_env_variable("CHATGPT_API_ENDPOINT")
        self.model = "gpt-3.5-turbo"
        logger.info("ChatGPTAPIClient initialized")

    @log_execution_time
    async def evaluate(
        self, system_message: str, prompt: str, max_tokens: int = 20
    ) -> float:
        logger.info(f"Evaluating prompt: {prompt[:50]}...")
        headers = self._get_headers()
        data = self._prepare_request_data(
            prompt, system_message=system_message, max_tokens=max_tokens
        )

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

    async def generate_text(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int = environment_config.MAX_TOKENS,
    ) -> str:
        logger.info(f"Generating text for prompt: {prompt[:50]}...")
        headers = self._get_headers()
        data = self._prepare_request_data(
            prompt, system_message=system_message, max_tokens=max_tokens
        )

        print("Generating argument from CHATGPT API")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint, headers=headers, json=data
                ) as response:
                    await self._check_response(response)
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    logger.info("Text generation completed")
                    return content
        except ClientError as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _prepare_request_data(
        self, prompt: str, system_message: str = None, max_tokens: int = 0
    ) -> Dict[str, Any]:
        if system_message:
            return {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
            }
        else:
            return {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
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

    def _extract_score(self, response: dict) -> float:
        try:
            content = (
                response.get("choices", [{}])[0].get("message", {}).get("content", "")
            )

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
