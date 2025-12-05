import operator
from collections import Counter
from collections.abc import Callable, Hashable, Mapping
from typing import Any, Union

import networkx as nx
from loguru import logger
from mappingtools.transformers import simplify
from networkx.classes.reportviews import EdgeDataView, EdgeView, NodeDataView, NodeView

from .. import color
from ..enums import GraphType
from ..modeling import GraphModel, Multiplicity
from ..tools import utcnow
from ..typing import NodeTypeAbsoluteId, UniverseNode
from ._builder import Builder


class NetworkxBuilder(Builder):
    """Build a NetworkX Graph"""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)
        self._graph: nx.Graph | None = None

    def _initialize_graph(self):
        """Initialize an empty NetworkX graph with metadata and default attributes."""
        self._graph: nx.Graph = self.graph_type.value(name=self.model.name,
                                                      node_types=Counter(),
                                                      edge_types=Counter())

    def _graph_edges(self, data, default=None):
        params = {'data': data, 'default': default}

        if isinstance(self._graph, nx.MultiGraph):
            params['keys'] = True

        return self._graph.edges(**params)

    def _populate_node_type(self, node_type: Union[Hashable, UniverseNode] = UniverseNode, **kwargs):
        for parent_node_type, child_node_types in self.model.node_children_types(node_type).items():
            for child_node_type in child_node_types:
                node_type_absolute_id = (parent_node_type, child_node_type)
                self._populate_nodes(node_type_absolute_id, **kwargs)

    @staticmethod
    def _parent_node_id(node_type_absolute_id: NodeTypeAbsoluteId, **kwargs: Any):
        if node_type_absolute_id[0] is UniverseNode:
            return UniverseNode

        ids = []
        for k, v in kwargs.items():
            if k[:-3] == node_type_absolute_id[1]:
                break
            ids.append(v)

        return tuple(ids)

    def _populate_nodes(self, node_type_absolute_id: NodeTypeAbsoluteId, **kwargs: Any):
        """Populate graph nodes based on the provided model and ID."""
        for node_model in self.model.node_models[node_type_absolute_id]:
            unique = node_model.uniqueness
            for node in node_model.generator(**kwargs):
                parent_node_id = self._parent_node_id(node_type_absolute_id, **kwargs)
                node_lineage = (*parent_node_id, node.key) if parent_node_id is not UniverseNode else (node.key,)
                node_id = (node.key,) if unique else node_lineage

                label = node.key
                if node_model.label is not None:
                    label = node_model.label(node.value) if callable(node_model.label) else node_model.label

                node_type = node.__class__.__name__.lower()
                if node_type == 'tuple':
                    node_type = node_model.type.lower()

                if node_id in self._graph:
                    logger.debug("Updating node. ID: {}, Label: {}", node_id, label)

                    match node_model.multiplicity:
                        case Multiplicity.ADD:
                            self._graph.nodes[node_id]['value'] = [self._graph.nodes[node_id]['value'] + node.value]
                        case Multiplicity.ALL:
                            self._graph.nodes[node_id]['value'].append(node.value)
                        case Multiplicity.FIRST:
                            ...
                        case Multiplicity.LAST:
                            self._graph.nodes[node_id]['value'] = [node.value]

                    self._graph.nodes[node_id]['magnitude'] += 1
                    self._graph.nodes[node_id]['updated'] = utcnow()
                else:
                    logger.debug("Adding node. ID: {}, Label: {}", node_id, label)
                    self._graph.add_node(node_id,
                                         label=label,
                                         type=node_type,
                                         value=[node.value],
                                         magnitude=1,
                                         lineage=list(node_lineage),
                                         created=utcnow())

                    self._graph.graph['node_types'].update({node_type: 1})

                if node_model.parent_type is not UniverseNode:
                    logger.debug("Adding edge. Source: {}, Target: {}", parent_node_id, node_id)
                    self._graph.add_edge(parent_node_id,
                                         node_id,
                                         created=utcnow())

                new_kwargs = kwargs.copy()
                new_kwargs[f"{node_type}_id"] = node.key
                self._populate_node_type(node_model.type, **new_kwargs)

    def _populate_edges(self, **kwargs: Any):
        """Populate graph edges based on defined connections."""
        for edge_model, edge_generators in self.model.edge_generators.items():
            for edge_generator in edge_generators:
                for edge in edge_generator(**kwargs):
                    edge_id = ((edge.source,), (edge.target,))
                    edge_label = edge.label(edge_id) if callable(edge.label) else edge.label
                    edge_weight = edge.weight or 1.0
                    edge_type = edge.type.lower()
                    logger.debug("Adding edge. Source: {}, Target: {}", *edge_id)

                    if isinstance(self._graph, nx.MultiGraph) or edge_id not in self._graph.edges:
                        self._graph.add_edge(*edge_id,
                                             label=edge_label,
                                             type=edge_type,
                                             value=[edge.value],
                                             weight=edge_weight,
                                             created=utcnow())
                        self._graph.graph['edge_types'].update({edge_type: 1})
                    else:
                        self._graph.edges[edge_id]['value'].append(edge.value)
                        self._graph.edges[edge_id]['weight'] += edge_weight
                        self._graph.edges[edge_id]['updated'] = utcnow()

    @staticmethod
    def _rectified_values(name: str, default: Any, elements: Callable[
        [str, Any], NodeView[Any] | EdgeView[Any] | NodeDataView[Any] | EdgeDataView], k: Callable[[Any], Any],
                          v: Callable[[Any], Any]) -> dict:
        if callable(default):
            elem = elements(data=name, default=None)
            return {k(e): default(k(e))
                    for e in elem
                    if (v(e) is None if isinstance(elem, NodeDataView) else v(e) is not None)}
        elif isinstance(default, dict):
            return default
        elif default:
            return {k(e): v(e) for e in elements(data=name, default=default) if v(e) == default}
        else:  # default is None or empty collection
            return {k(e): k(e) for e in elements(data=name, default=default) if v(e) is default}

    def _rectify_node_attributes(self, **defaults):
        for name, default in defaults.items():
            if values := self._rectified_values(
                    name,
                    default,
                    self._graph.nodes,
                    operator.itemgetter(0),
                    operator.itemgetter(1),
            ):
                nx.set_node_attributes(self._graph, values=values, name=name)

        if default_type := defaults.get('type'):
            type_count = sum(1 for n, d in self._graph.nodes(data='type') if d == default_type)
            if type_count:
                self._graph.graph['node_types'].update({default_type: type_count})

    def _rectify_edge_attributes(self, **defaults):
        for name, default in defaults.items():
            if values := self._rectified_values(
                    name,
                    default,
                    self._graph_edges,
                    lambda x: tuple(x[:-1]),
                    lambda x: x[-1]
            ):
                nx.set_edge_attributes(self._graph, values=values, name=name)

        if default_type := defaults.get('type'):
            type_count = sum(1 for *_, d in self._graph_edges(data='type') if d == default_type)
            if type_count:
                self._graph.graph['edge_types'].update({default_type: type_count})

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
        self.model.rectify(_type=default_type, parent_type=default_type, label=default_label)

    def _build_graph(self, node_attributes: Mapping, **kwargs: Any):
        self._initialize_graph()
        self._populate_node_type(**kwargs)
        self._populate_edges(**kwargs)
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
