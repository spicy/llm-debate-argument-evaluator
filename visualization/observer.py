"""
TODO: This module...
"""

from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        """TODO: Add Simple Docstring"""
        pass


class Subject:
    def __init__(self):
        """TODO: Add Simple Docstring"""
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        """TODO: Add Simple Docstring"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        """TODO: Add Simple Docstring"""
        self._observers.remove(observer)

    def notify(self):
        """TODO: Add Simple Docstring"""
        for observer in self._observers:
            observer.update(self)
