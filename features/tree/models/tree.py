"""
Tree model - Represents tree metadata and provides tree operations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Tree:
    """
    Represents a debate argument tree with metadata.

    A Tree contains metadata about an argument tree including its name, topic,
    description, and organizational information. Each tree can contain multiple
    argument nodes that form a hierarchical debate structure.
    """

    id: Optional[UUID] = None
    name: str = ""
    topic: str = ""
    description: Optional[str] = None
    root_node_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate tree data after initialization."""
        if not self.name.strip():
            raise ValueError("Tree name cannot be empty")
        if not self.topic.strip():
            raise ValueError("Tree topic cannot be empty")

    @property
    def has_root_node(self) -> bool:
        """Check if this tree has a root node assigned."""
        return self.root_node_id is not None

    @property
    def display_name(self) -> str:
        """Get a display-friendly name for the tree."""
        return f"{self.name} ({self.topic})"

    def to_dict(self) -> dict:
        """Convert tree to dictionary format for database operations."""
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "topic": self.topic,
            "description": self.description,
            "root_node_id": self.root_node_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tree":
        """Create Tree instance from dictionary data."""
        # Convert string UUID back to UUID object if present
        tree_id = None
        if data.get("id"):
            tree_id = UUID(data["id"]) if isinstance(data["id"], str) else data["id"]

        # Convert ISO string timestamps back to datetime objects
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            else:
                created_at = data["created_at"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(
                    data["updated_at"].replace("Z", "+00:00")
                )
            else:
                updated_at = data["updated_at"]

        return cls(
            id=tree_id,
            name=data["name"],
            topic=data["topic"],
            description=data.get("description"),
            root_node_id=data.get("root_node_id"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self) -> str:
        """String representation of the tree."""
        return self.display_name

    def __repr__(self) -> str:
        """Developer-friendly representation of the tree."""
        return f"Tree(id={self.id}, name='{self.name}', topic='{self.topic}')"
