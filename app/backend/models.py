"""
Resource data model for For-All.

OOP model using dataclass for clean, type-safe resource representation.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Resource:
    """Resource model representing community organizations."""
    id: int
    name: str
    category: str  # "housing", "food", or "clothing"
    address: str
    city: str
    state: str
    phone: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert Resource to plain dictionary for JSON serialization."""
        return asdict(self)

