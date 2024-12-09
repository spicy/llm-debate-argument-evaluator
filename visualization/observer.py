from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass


class Subject:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)


class DebateTreeSubject(Subject):
    def __init__(self):
        super().__init__()
        self._debate_tree = {}
        self.optimal_path: List[Dict[str, Any]] = []

    @property
    def debate_tree(self):
        return self._debate_tree

    @debate_tree.setter
    def debate_tree(self, value):
        self._debate_tree = value
        self.notify()
