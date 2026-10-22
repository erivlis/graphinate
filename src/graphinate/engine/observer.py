"""Observer protocol for receiving GraphEngine execution events."""

from typing import Protocol, runtime_checkable

from .events import EdgeEvent, NodeEvent


@runtime_checkable
class GraphObserver(Protocol):
    """Protocol for observers subscribed to GraphEngine execution lifecycle events."""

    def on_start(self, name: str) -> None:
        """Called when graph execution starts."""
        ...  # pragma: no cover

    def on_node(self, event: NodeEvent) -> None:
        """Called when a node is generated."""
        ...  # pragma: no cover

    def on_edge(self, event: EdgeEvent) -> None:
        """Called when an edge is generated."""
        ...  # pragma: no cover

    def on_finish(self) -> None:
        """Called when graph execution completes."""
        ...  # pragma: no cover


__all__ = ('GraphObserver',)
