from config import evaluation_config
from evaluation.model_factory import ModelFactory
from utils.logger import log_execution_time, logger


class EvaluationService:
    def __init__(self, model_factory: ModelFactory):
        self.model_factory = model_factory
        logger.info("EvaluationService initialized")

    @log_execution_time
    async def evaluate_argument(self, argument: str):
        logger.info(f"Evaluating argument: {argument[:50]}...")
        models = self.model_factory.get_models()
        evaluations = {}

        for model_name, model in models.items():
            logger.debug(f"Evaluating with model: {model_name}")
            coherence = await model.evaluate_coherence(argument)
            persuasion = await model.evaluate_persuasion(argument)
            cultural_acceptance = await model.evaluate_cultural_acceptance(argument)
            factual_accuracy = await model.evaluate_factual_accuracy(argument)

            evaluations[model_name] = {
                evaluation_config.COHERENCE: coherence,
                evaluation_config.PERSUASION: persuasion,
                evaluation_config.CULTURAL_ACCEPTANCE: cultural_acceptance,
                evaluation_config.FACTUAL_ACCURACY: factual_accuracy,
            }
            logger.debug(
                f"Evaluation results for {model_name}: {evaluations[model_name]}"
            )

        logger.info("Argument evaluation completed")
        return evaluations
