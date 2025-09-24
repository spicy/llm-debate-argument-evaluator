"""
TODO: This module...
"""

from typing import Dict

from config.base_config import BaseConfig


class PriorityQueueConfig(BaseConfig):
    PRIORITY_LEVELS: Dict[str, int] = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}


priority_queue_config: PriorityQueueConfig = PriorityQueueConfig()
