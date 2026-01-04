import inspect
from dataclasses import dataclass
from typing import Protocol

from .modeling import GraphModel

# region Events

@dataclass
class GraphEvent:
    """Base class for all graph execution events."""


@dataclass
class NodeEvent(GraphEvent):
    """Emitted when a node is discovered/created."""
    id: str
    data: dict
    parent_id: str | None = None


@dataclass
class EdgeEvent(GraphEvent):
    """Emitted when an edge is discovered/created."""
    source_id: str
    target_id: str
    data: dict


@dataclass
class ErrorEvent(GraphEvent):
    """Emitted when a generator raises an exception."""
    error: Exception
    context: dict


# endregion

# region Interfaces

class GraphObserver(Protocol):
    """Interface for components that listen to the GraphEngine."""

    async def on_node(self, event: NodeEvent) -> None:
        ...

    async def on_edge(self, event: EdgeEvent) -> None:
        ...

    async def on_error(self, event: ErrorEvent) -> None:
        ...

    async def on_complete(self) -> None:
        ...


# endregion

# region Engine

class GraphEngine:
    """The Execution Engine.

    Responsible for iterating over the GraphModel, handling the 'magic'
    (ID generation, dependency injection), and notifying observers.
    """

    def __init__(self, model: GraphModel):
        self.model = model
        self._observers: list[GraphObserver] = []
        self._is_running = False

    def subscribe(self, observer: GraphObserver):
        """Register an observer to receive events."""
        self._observers.append(observer)

    async def run(self):
        """Execute the graph generation process."""
        if self._is_running:
            raise RuntimeError("Engine is already running")

        self._is_running = True

        try:
            # TODO: This is where the logic from NetworkxBuilder._populate_nodes moves to.
            # It will need to handle:
            # 1. Root nodes
            # 2. Recursive children
            # 3. Async vs Sync generators (GEP-023)

            # Mock implementation for scaffold
            await self._notify_node("root", {"label": "Root"}, None)

        except Exception as e:
            await self._notify_error(e)
        finally:
            await self._notify_complete()
            self._is_running = False

    # region Internal Notification Helpers

    async def _notify_node(self, node_id: str, data: dict, parent_id: str | None):
        event = NodeEvent(id=node_id, data=data, parent_id=parent_id)
        await self._broadcast(lambda obs: obs.on_node(event))

    async def _notify_edge(self, source: str, target: str, data: dict):
        event = EdgeEvent(source_id=source, target_id=target, data=data)
        await self._broadcast(lambda obs: obs.on_edge(event))

    async def _notify_error(self, error: Exception):
        event = ErrorEvent(error=error, context={})
        await self._broadcast(lambda obs: obs.on_error(event))

    async def _notify_complete(self):
        await self._broadcast(lambda obs: obs.on_complete())

    async def _broadcast(self, callback):
        """Notify all observers.

        Design Decision: Sequential await.
        If one observer is slow, it slows down the engine (Backpressure).
        This is usually desired to prevent OOM.
        """
        for observer in self._observers:
            if inspect.iscoroutinefunction(callback):
                await callback(observer)
            else:
                # Handle synchronous observers if we allow them
                res = callback(observer)
                if inspect.isawaitable(res):
                    await res

    # endregion
