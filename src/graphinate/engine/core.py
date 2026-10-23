"""Core GraphEngine implementation decoupling traversal and event generation from storage."""

import inspect
from collections.abc import AsyncIterable, Hashable
from typing import Any, Union

from loguru import logger

from ..modeling import GraphModel, GraphModelError, NodeModel
from ..typing import Extractor, NodeTypeAbsoluteId, UniverseNode
from .events import EdgeEvent, NodeEvent
from .observer import GraphObserver


class GraphEngine:
    """Observable execution engine for traversing a GraphModel and dispatching node/edge events."""

    def __init__(
        self,
        model: GraphModel,
        *,
        compile_model: bool = True,
        default_type: Extractor | None = None,
        parent_type: str | None = UniverseNode,
        key: Extractor | None = None,
        value: Extractor | None = None,
        label: Extractor | None = None,
    ):
        """Initialize the GraphEngine.

        Args:
            model: The GraphModel to execute.
            compile_model: If True (default), compiles a validated clone of the model.
            default_type: Optional fallback node type for edge-only models during compilation.
            parent_type: Optional fallback parent node type for edge-only models.
            key: Optional fallback key extractor for edge-only models.
            value: Optional fallback value extractor for edge-only models.
            label: Optional fallback label extractor for edge-only models.
        """
        if compile_model:
            self.model = model.compile(
                _type=default_type,
                parent_type=parent_type,
                key=key,
                value=value,
                label=label,
            )
        else:
            self.model = model
        self._observers: list[GraphObserver] = []

    def subscribe(self, observer: GraphObserver) -> None:
        """Register a GraphObserver to receive execution events."""
        self._observers.append(observer)

    def _emit_start(self) -> None:
        for observer in self._observers:
            observer.on_start(self.model.name)

    def _emit_node(self, event: NodeEvent) -> None:
        for observer in self._observers:
            observer.on_node(event)

    def _emit_edge(self, event: EdgeEvent) -> None:
        for observer in self._observers:
            observer.on_edge(event)

    def _emit_finish(self) -> None:
        for observer in self._observers:
            observer.on_finish()

    @staticmethod
    def _parent_node_id(node_type_absolute_id: NodeTypeAbsoluteId, **kwargs: Any) -> Any:
        parent_type = node_type_absolute_id[0]
        if parent_type is UniverseNode:
            return UniverseNode

        parent_type_lower = parent_type.lower() if isinstance(parent_type, str) else parent_type
        ids = []
        for k, v in kwargs.items():
            if k.endswith('_id'):
                ids.append(v)
                if k[:-3].lower() == parent_type_lower:
                    break

        return tuple(ids)

    def _resolve_parent_node_id(
        self,
        node_model: NodeModel,
        node_type_absolute_id: NodeTypeAbsoluteId,
        _lineage: tuple | None,
        **kwargs: Any,
    ) -> Any:
        if node_model.parent_type is UniverseNode:
            return UniverseNode
        if _lineage is not None:
            return _lineage
        return self._parent_node_id(node_type_absolute_id, **kwargs)

    def _handle_generated_node(
        self,
        node: Any,
        node_model: NodeModel,
        parent_node_id: Any,
        is_label_callable: bool,
    ) -> tuple[tuple[Hashable, ...], str]:
        node_lineage = (*parent_node_id, node.key) if parent_node_id is not UniverseNode else (node.key,)
        node_id = (node.key,) if node_model.uniqueness else node_lineage

        label = node.key
        if node_model.label is not None:
            label = node_model.label(node.value) if is_label_callable else node_model.label

        node_type = node.__class__.__name__.lower()
        if node_type == 'tuple':
            node_type = node_model.type.lower()

        self._emit_node(
            NodeEvent(
                node_id=node_id,
                type=node_type,
                label=label,
                value=node.value,
                magnitude=1,
                lineage=node_lineage,
                multiplicity=node_model.multiplicity,
            )
        )

        if node_model.parent_type is not UniverseNode:
            self._emit_edge(
                EdgeEvent(
                    source_id=parent_node_id,
                    target_id=node_id,
                    is_hierarchy=True,
                )
            )
        return node_id, node_type

    def _handle_generated_edge(self, edge: Any) -> None:
        source_id = (edge.source,)
        target_id = (edge.target,)
        edge_id = (source_id, target_id)
        edge_label = edge.label(edge_id) if callable(edge.label) else edge.label
        edge_weight = edge.weight or 1.0
        edge_type = edge.type.lower()
        self._emit_edge(
            EdgeEvent(
                source_id=source_id,
                target_id=target_id,
                type=edge_type,
                label=edge_label,
                value=edge.value,
                weight=edge_weight,
                is_hierarchy=False,
            )
        )

    def _populate_node_type(
        self,
        node_type: Union[Hashable, UniverseNode] = UniverseNode,
        _lineage: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        for parent_node_type, child_node_types in self.model.node_children_types(node_type).items():
            for child_node_type in child_node_types:
                node_type_absolute_id = (parent_node_type, child_node_type)
                self._populate_nodes(node_type_absolute_id, _lineage=_lineage, **kwargs)

    def _populate_nodes(
        self,
        node_type_absolute_id: NodeTypeAbsoluteId,
        _lineage: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        """Traverse node generators for the given absolute ID and emit NodeEvent/EdgeEvent objects."""
        for node_model in self.model.node_models[node_type_absolute_id]:
            is_label_callable = callable(node_model.label)
            parent_node_id = self._resolve_parent_node_id(node_model, node_type_absolute_id, _lineage, **kwargs)

            gen = node_model.generator(**kwargs)
            if isinstance(gen, AsyncIterable) or inspect.isawaitable(gen):
                raise GraphModelError(
                    f"Node generator for type '{node_model.type}' is asynchronous. "
                    "Use `await engine.arun(...)` or `await builder.abuild(...)` instead."
                )

            for node in gen:
                node_id, node_type = self._handle_generated_node(
                    node, node_model, parent_node_id, is_label_callable
                )
                new_kwargs = kwargs.copy()
                new_kwargs[f'{node_type}_id'] = node.key
                self._populate_node_type(node_model.type, _lineage=node_id, **new_kwargs)
                if node_type != node_model.type.lower():
                    self._populate_node_type(node_type, _lineage=node_id, **new_kwargs)

    def _populate_edges(self, **kwargs: Any) -> None:
        """Traverse edge generators and emit EdgeEvent objects."""
        for edge_model, edge_generators in self.model.edge_generators.items():
            logger.debug("Adding from {}", edge_model)
            for edge_generator in edge_generators:
                gen = edge_generator(**kwargs)
                if isinstance(gen, AsyncIterable) or inspect.isawaitable(gen):
                    raise GraphModelError(
                        f"Edge generator for type '{edge_model}' is asynchronous. "
                        "Use `await engine.arun(...)` or `await builder.abuild(...)` instead."
                    )
                for edge in gen:
                    self._handle_generated_edge(edge)

    async def _apopulate_node_type(
        self,
        node_type: Union[Hashable, UniverseNode] = UniverseNode,
        _lineage: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        for parent_node_type, child_node_types in self.model.node_children_types(node_type).items():
            for child_node_type in child_node_types:
                node_type_absolute_id = (parent_node_type, child_node_type)
                await self._apopulate_nodes(node_type_absolute_id, _lineage=_lineage, **kwargs)

    async def _apopulate_nodes(
        self,
        node_type_absolute_id: NodeTypeAbsoluteId,
        _lineage: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        """Asynchronously traverse sync or async node generators and emit events."""
        for node_model in self.model.node_models[node_type_absolute_id]:
            is_label_callable = callable(node_model.label)
            parent_node_id = self._resolve_parent_node_id(node_model, node_type_absolute_id, _lineage, **kwargs)

            gen = node_model.generator(**kwargs)

            if isinstance(gen, AsyncIterable):
                async for node in gen:
                    node_id, node_type = self._handle_generated_node(
                        node, node_model, parent_node_id, is_label_callable
                    )
                    new_kwargs = kwargs.copy()
                    new_kwargs[f'{node_type}_id'] = node.key
                    await self._apopulate_node_type(node_model.type, _lineage=node_id, **new_kwargs)
                    if node_type != node_model.type.lower():
                        await self._apopulate_node_type(node_type, _lineage=node_id, **new_kwargs)
            else:
                for node in gen:
                    node_id, node_type = self._handle_generated_node(
                        node, node_model, parent_node_id, is_label_callable
                    )
                    new_kwargs = kwargs.copy()
                    new_kwargs[f'{node_type}_id'] = node.key
                    await self._apopulate_node_type(node_model.type, _lineage=node_id, **new_kwargs)
                    if node_type != node_model.type.lower():
                        await self._apopulate_node_type(node_type, _lineage=node_id, **new_kwargs)

    async def _apopulate_edges(self, **kwargs: Any) -> None:
        """Asynchronously traverse sync or async edge generators and emit EdgeEvent objects."""
        for edge_model, edge_generators in self.model.edge_generators.items():
            logger.debug("Adding from {}", edge_model)
            for edge_generator in edge_generators:
                gen = edge_generator(**kwargs)

                if isinstance(gen, AsyncIterable):
                    async for edge in gen:
                        self._handle_generated_edge(edge)
                else:
                    for edge in gen:
                        self._handle_generated_edge(edge)

    def run(self, **kwargs: Any) -> None:
        """Execute the graph model synchronously and dispatch events to all subscribed observers."""
        self._emit_start()
        self._populate_node_type(**kwargs)
        self._populate_edges(**kwargs)
        self._emit_finish()

    async def arun(self, **kwargs: Any) -> None:
        """Execute the graph model asynchronously and dispatch events to all subscribed observers."""
        self._emit_start()
        await self._apopulate_node_type(**kwargs)
        await self._apopulate_edges(**kwargs)
        self._emit_finish()


__all__ = ('GraphEngine',)

