"""Data contracts for GraphEngine lifecycle events."""

from collections.abc import Hashable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..enums import Multiplicity
from ..tools import utcnow


@dataclass(frozen=True, slots=True)
class NodeEvent:
    """Event emitted when a graph node is generated during engine execution."""

    node_id: tuple[Hashable, ...]
    type: str
    label: Any
    value: Any
    magnitude: int = 1
    lineage: tuple[Hashable, ...] = ()
    multiplicity: Multiplicity = Multiplicity.ALL
    created: datetime = field(default_factory=utcnow)


@dataclass(frozen=True, slots=True)
class EdgeEvent:
    """Event emitted when a graph edge is generated during engine execution."""

    source_id: tuple[Hashable, ...]
    target_id: tuple[Hashable, ...]
    type: str | None = None
    label: Any = None
    value: Any = None
    weight: float = 1.0
    is_hierarchy: bool = False
    created: datetime = field(default_factory=utcnow)


__all__ = ('EdgeEvent', 'NodeEvent')
