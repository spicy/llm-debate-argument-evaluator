"""
This module provides a generic implementation of the Subject for the observer pattern.
"""

import asyncio
from typing import List
from visualization.observer import Observer


class Subject:
    """A class that implements the Subject part of the observer pattern."""

    def __init__(self):
        """Initializes the Subject with an empty list of observers."""
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer):
        """Adds an observer to the list."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        """Removes an observer from the list."""
        self._observers.remove(observer)

    async def notify(self, *args, **kwargs):
        """Asynchronously notifies all observers of a change."""
        tasks = []
        for observer in self._observers:
            tasks.append(observer.update(*args, **kwargs))
        await asyncio.gather(*tasks)
