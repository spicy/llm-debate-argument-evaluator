from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class QueueServiceInterface(ABC):
    @property
    @abstractmethod
    def debate_tree(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def add_node(self, node: Dict[str, Any], priority: str = "MEDIUM") -> None:
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all_nodes(self) -> Dict[str, Dict[str, Any]]:
        pass

    @abstractmethod
    def update_node(self, node_id: str, node_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def node_exists(self, node_id: str) -> bool:
        pass

    @abstractmethod
    def get_unique_id(self) -> int:
        pass

    @abstractmethod
    def attach(self, observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass
