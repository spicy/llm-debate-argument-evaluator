class LoggerConfig:
    LOGGER_NAME = "llm_debate_evaluator"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGS_FOLDER = "logs"
    LAST_FILE_NAME = "last.log"
    LOG_FILE_NAME = "app.log"


logger_config = LoggerConfig()
