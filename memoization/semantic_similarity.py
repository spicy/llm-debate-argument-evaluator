from sentence_transformers import SentenceTransformer, util

from utils.logger import log_execution_time, logger


class SemanticSimilarity:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        logger.info(f"SemanticSimilarity initialized with model: {model_name}")

    @log_execution_time
    async def calculate_similarity(self, argument1: str, argument2: str) -> float:
        logger.debug(
            f"Calculating similarity between arguments: '{argument1[:50]}...' and '{argument2[:50]}...'"
        )
        embedding1 = self.model.encode(argument1, convert_to_tensor=True)
        embedding2 = self.model.encode(argument2, convert_to_tensor=True)

        similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
        logger.debug(f"Similarity calculated: {similarity}")
        return similarity
