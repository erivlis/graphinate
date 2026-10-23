from collections import Counter
from collections.abc import Hashable, Mapping
from typing import Any

import networkx as nx
from loguru import logger
from mappingtools.transformers import simplify

from .. import color
from ..engine import EdgeEvent, GraphEngine, GraphObserver, NodeEvent
from ..enums import GraphType, Multiplicity
from ..modeling import GraphModel
from ..tools import utcnow
from ..typing import NodeTypeAbsoluteId, UniverseNode
from .builder import Builder


class NetworkxBuilder(Builder, GraphObserver):
    """Build a NetworkX Graph by observing a GraphEngine run."""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)
        self._graph: nx.Graph | None = None

    def _initialize_graph(self, name: str | None = None):
        """Initialize an empty NetworkX graph with metadata and default attributes."""
        graph_name = self.model.name if name is None else name
        self._graph: nx.Graph = self.graph_type.value(
            name=graph_name,
            node_types=Counter(),
            edge_types=Counter(),
        )

    def on_start(self, name: str) -> None:
        """Called when GraphEngine execution starts."""
        self._initialize_graph(name=name)

    def on_node(self, event: NodeEvent) -> None:
        """Mutate the in-memory NetworkX graph in response to a NodeEvent."""
        node_id = event.node_id
        label = event.label
        node_type = event.type

        if node_id in self._graph:
            logger.debug('Updating node. ID: {}, Label: {}', node_id, label)

            match event.multiplicity:
                case Multiplicity.ADD:
                    self._graph.nodes[node_id]['value'] = [self._graph.nodes[node_id]['value'] + event.value]
                case Multiplicity.ALL:
                    self._graph.nodes[node_id]['value'].append(event.value)
                case Multiplicity.FIRST:
                    ...
                case Multiplicity.LAST:
                    self._graph.nodes[node_id]['value'] = [event.value]

            self._graph.nodes[node_id]['magnitude'] += event.magnitude
            self._graph.nodes[node_id]['updated'] = utcnow()
        else:
            logger.debug('Adding node. ID: {}, Label: {}', node_id, label)
            self._graph.add_node(
                node_id,
                label=label,
                type=node_type,
                value=[event.value],
                magnitude=event.magnitude,
                lineage=list(event.lineage),
                created=event.created,
            )

            self._graph.graph['node_types'][node_type] += 1

    def on_edge(self, event: EdgeEvent) -> None:
        """Add or update an edge in the in-memory NetworkX graph in response to an EdgeEvent."""
        if event.is_hierarchy:
            logger.debug('Adding edge. Source: {}, Target: {}', event.source_id, event.target_id)
            self._graph.add_edge(event.source_id, event.target_id, created=event.created)
            return

        edge_id = (event.source_id, event.target_id)
        edge_type = event.type.lower() if event.type else 'edge'
        logger.debug('Adding edge. Source: {}, Target: {}', *edge_id)

        if (
            isinstance(self._graph, nx.MultiGraph)
            or edge_id not in self._graph.edges
            or 'value' not in self._graph.edges[edge_id]
        ):
            self._graph.add_edge(
                *edge_id,
                label=event.label,
                type=edge_type,
                value=[event.value],
                weight=event.weight,
                created=event.created,
            )
            self._graph.graph['edge_types'][edge_type] += 1
        else:
            self._graph.edges[edge_id]['value'].append(event.value)
            self._graph.edges[edge_id]['weight'] += event.weight
            self._graph.edges[edge_id]['updated'] = utcnow()

    def on_finish(self) -> None:
        """Called when GraphEngine execution completes."""

    def _graph_edges(self, data, default=None):
        params = {'data': data, 'default': default}

        if isinstance(self._graph, nx.MultiGraph):
            params['keys'] = True

        return self._graph.edges(**params)

    @staticmethod
    def _parent_node_id(node_type_absolute_id: NodeTypeAbsoluteId, **kwargs: Any):
        return GraphEngine._parent_node_id(node_type_absolute_id, **kwargs)

    def _populate_node_type(
        self,
        node_type: Hashable | UniverseNode = UniverseNode,
        _lineage: tuple | None = None,
        **kwargs: Any,
    ):
        engine = GraphEngine(self.model, compile_model=False)
        engine.subscribe(self)
        engine._populate_node_type(node_type=node_type, _lineage=_lineage, **kwargs)

    def _populate_nodes(
        self,
        node_type_absolute_id: NodeTypeAbsoluteId,
        _lineage: tuple | None = None,
        **kwargs: Any,
    ):
        """Populate graph nodes based on the provided model and ID by delegating to GraphEngine."""
        engine = GraphEngine(self.model, compile_model=False)
        engine.subscribe(self)
        engine._populate_nodes(node_type_absolute_id, _lineage=_lineage, **kwargs)

    def _populate_edges(self, **kwargs: Any):
        """Populate graph edges based on defined connections by delegating to GraphEngine."""
        engine = GraphEngine(self.model, compile_model=False)
        engine.subscribe(self)
        engine._populate_edges(**kwargs)

    def _apply_defaults(self, elements_iter, defaults: Mapping, is_node: bool):
        """Apply defaults to elements in a single pass."""
        type_count = 0
        default_type = defaults.get('type')

        # Pre-sort defaults into static and callable to avoid repeated checks
        static_defaults = []
        callable_defaults = []
        for name, default in defaults.items():
            if callable(default):
                callable_defaults.append((name, default))
            else:
                static_defaults.append((name, default))

        for *keys, data in elements_iter:
            element_id = keys[0] if is_node else tuple(keys)

            # Apply static defaults
            for name, default in static_defaults:
                if name not in data:
                    # Truthy static else Falsy static (e.g. value=[]) -> Set ID
                    data[name] = default if default else element_id

            # Apply callable defaults
            for name, default in callable_defaults:
                val = data.get(name)
                if is_node:
                    if val is None:
                        data[name] = default(element_id)
                else:
                    if val is not None:
                        data[name] = default(element_id)

            if default_type and data.get('type') == default_type:
                type_count += 1

        if default_type and type_count > 0:
            counter_name = 'node_types' if is_node else 'edge_types'
            self._graph.graph[counter_name][default_type] += type_count

    def _rectify_node_attributes(self, **defaults):
        simple_defaults = {}
        for name, default in defaults.items():
            if isinstance(default, dict):
                nx.set_node_attributes(self._graph, values=default, name=name)
            else:
                simple_defaults[name] = default

        if simple_defaults:
            self._apply_defaults(self._graph.nodes(data=True), simple_defaults, is_node=True)

    def _rectify_edge_attributes(self, **defaults):
        simple_defaults = {}
        for name, default in defaults.items():
            if isinstance(default, dict):
                nx.set_edge_attributes(self._graph, values=default, name=name)
            else:
                simple_defaults[name] = default

        if simple_defaults:
            self._apply_defaults(self._graph_edges(data=True), simple_defaults, is_node=False)

    def _finalize_graph(self, **node_attributes):
        self._rectify_node_attributes(**node_attributes)

        if 'color' not in node_attributes:
            self._rectify_node_attributes(color=color.node_color_mapping(self._graph))

        self._rectify_edge_attributes(**self.default_edge_attributes)

        for counter_name in ('node_types', 'edge_types'):
            counter = self._graph.graph[counter_name]
            self._graph.graph[counter_name] = simplify(counter)

        self._graph.graph['created'] = utcnow()

    def _rectify_model(self, node_attributes: Mapping):
        default_type = node_attributes.get('type')
        default_label = node_attributes.get('label')
        self.model = self.model.compile(_type=default_type, parent_type=default_type, label=default_label)

    def _build_graph(self, node_attributes: Mapping, **kwargs: Any):
        engine = GraphEngine(self.model, compile_model=False)
        engine.subscribe(self)
        engine.run(**kwargs)
        self._finalize_graph(**node_attributes)

    async def _abuild_graph(self, node_attributes: Mapping, **kwargs: Any):
        engine = GraphEngine(self.model, compile_model=False)
        engine.subscribe(self)
        await engine.arun(**kwargs)
        self._finalize_graph(**node_attributes)

    def build(self, **kwargs: Any) -> nx.Graph:
        """Build a NetworkX graph representation.

        Args:
            **kwargs:

        Returns:
            NetworkX Graph
        """
        super().build(**kwargs)

        default_node_attributes = dict(**self.default_node_attributes)
        if 'default_node_attributes' in kwargs:
            default_node_attributes.update(kwargs.pop('default_node_attributes') or {})

        self._rectify_model(default_node_attributes)
        self._build_graph(default_node_attributes, **kwargs)
        return self._graph

    async def abuild(self, **kwargs: Any) -> nx.Graph:
        """Asynchronously build a NetworkX graph representation.

        Args:
            **kwargs:

        Returns:
            NetworkX Graph
        """
        await super().abuild(**kwargs)

        default_node_attributes = dict(**self.default_node_attributes)
        if 'default_node_attributes' in kwargs:
            default_node_attributes.update(kwargs.pop('default_node_attributes') or {})

        self._rectify_model(default_node_attributes)
        await self._abuild_graph(default_node_attributes, **kwargs)
        return self._graph


