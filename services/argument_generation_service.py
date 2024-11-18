import random
from typing import Dict, List

from evaluation.api_clients.base_api_client import BaseAPIClient
from utils.async_utils import run_async_tasks
from utils.logger import log_execution_time, logger


class ArgumentGenerationService:
    def __init__(self, api_client: BaseAPIClient):
        self.prompts = {
            "abortion": {
                "Women's Rights": {
                    "supporting": [
                        "How does access to abortion support women's bodily autonomy?",
                        "What are the positive socioeconomic implications of abortion access for women?",
                    ],
                    "against": [
                        "How might unrestricted abortion access negatively impact women's mental health?",
                        "What are potential risks of using abortion as a primary form of birth control?",
                    ],
                },
                "Fetal Rights": {
                    "supporting": [
                        "At what stage of development should a fetus be granted legal rights?",
                        "How can we balance fetal rights with maternal rights in a fair manner?",
                    ],
                    "against": [
                        "Why should a fetus be considered a person from the moment of conception?",
                        "How does granting full rights to a fetus impact the rights of the mother?",
                    ],
                },
            }
            # Add more topics and subcategories as needed
        }
        self.api_client = api_client
        logger.info("ArgumentGenerationService initialized")

    @log_execution_time
    async def generate_arguments(
        self, topic: str, subcategory: str, num_arguments_per_side: int = 3
    ) -> Dict[str, List[str]]:
        logger.info(
            f"Generating {num_arguments_per_side * 2} arguments for {topic} - {subcategory}"
        )
        if topic not in self.prompts or subcategory not in self.prompts[topic]:
            logger.error(f"Invalid topic or subcategory: {topic}, {subcategory}")
            raise ValueError(f"Invalid topic or subcategory: {topic}, {subcategory}")

        prompts_supporting = self.prompts[topic][subcategory]["supporting"]
        prompts_against = self.prompts[topic][subcategory]["against"]

        async def generate_single_argument(prompt: str, stance: str) -> str:
            system_message = (
                f"You are an AI assistant tasked with generating a balanced and "
                f"well-reasoned argument {stance} the topic. Provide a concise argument "
                f"based on the given prompt, considering the {stance} perspective."
                f"The argument should be a single argument and to the point."
            )
            response = await self.api_client.generate_text(
                system_message=system_message, user_message=prompt, max_tokens=150
            )
            return response.strip()

        # Generate arguments asynchronously
        tasks_supporting = [
            generate_single_argument(random.choice(prompts_supporting), "supporting")
            for _ in range(num_arguments_per_side)
        ]
        tasks_against = [
            generate_single_argument(random.choice(prompts_against), "against")
            for _ in range(num_arguments_per_side)
        ]

        arguments_supporting = await run_async_tasks(tasks_supporting)
        arguments_against = await run_async_tasks(tasks_against)

        for i, argument in enumerate(arguments_supporting + arguments_against):
            stance = "supporting" if i < num_arguments_per_side else "against"
            logger.debug(
                f"Generated {stance} argument {i % num_arguments_per_side + 1}: {argument[:50]}..."
            )
            logger.info(
                f"Generated {stance} argument {i % num_arguments_per_side + 1}: {argument}"
            )

        logger.info(
            f"Generated {len(arguments_supporting)} supporting arguments and {len(arguments_against)} arguments against"
        )
        return {"supporting": arguments_supporting, "against": arguments_against}
