"""
TODO: This module...
"""

from typing import Any, Dict

from utils.logger import logger


class DependencyRegistry:
    _instance = None
    dependencies: Dict[str, Any]

    def __new__(cls):
        """TODO: Add Simple Docstring"""
        if cls._instance is None:
            cls._instance = super(DependencyRegistry, cls).__new__(cls)
            cls._instance.dependencies = {}
        return cls._instance

    def register(self, name: str, dependency: Any) -> None:
        """TODO: Add Simple Docstring"""
        self.dependencies[name] = dependency
        logger.debug(f"Registered dependency: {name}")

    def get(self, name: str) -> Any:
        """TODO: Add Simple Docstring"""
        dependency = self.dependencies.get(name)
        if dependency:
            logger.debug(f"Retrieved dependency: {name}")
        else:
            logger.warning(f"Dependency not found: {name}")
        return dependency

    def clear(self) -> None:
        """TODO: Add Simple Docstring"""
        self.dependencies.clear()
        logger.debug("Cleared all dependencies")


# Global instance
dependency_registry = DependencyRegistry()
