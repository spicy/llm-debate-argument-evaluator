"""
TODO: This module...
"""

import supabase
from config.environment import get_env_variable
from utils.logger import logger


class SupabaseService:
    def __init__(self):
        """TODO: Add Simple Docstring"""
        try:
            self.client = supabase.create_client(
                get_env_variable("SUPABASE_URL"),
                get_env_variable("SUPABASE_SECRET_KEY"),
            )
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def get_client(self):
        """TODO: Add Simple Docstring"""
        return self.client
