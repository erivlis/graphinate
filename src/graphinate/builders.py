"""Builder classes that generate graph data structures from a GraphModel

  Attributes:
      GraphRepresentation (GraphRepresentation): GraphRepresentation Type
"""
import functools
import importlib
import inspect
import json
import math
import operator
from abc import ABC
from collections import Counter
from collections.abc import Callable, Hashable, Mapping
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Literal, Optional, Union

import inflect
import mappingtools
import networkx as nx
import networkx_mermaid as nxm
import strawberry
from loguru import logger
from mappingtools.transformers import simplify
from strawberry.extensions import ParserCache, QueryDepthLimiter, ValidationCache

from . import color, converters
from .converters import decode_edge_id, decode_id, edge_label_converter, encode_edge_id, encode_id, node_label_converter
from .modeling import GraphModel, Multiplicity
from .tools import utcnow
from .typing import NodeTypeAbsoluteId, UniverseNode

GraphRepresentation = Union[dict, nx.Graph, strawberry.Schema, nxm.typing.MermaidDiagram, str]  # noqa: UP007


class GraphType(Enum):
    """Graph Types

    The choice of graph class depends on the structure of the graph you want to represent.

    | **Graph Type** | **Type**   | **Self-loops allowed** | **Parallel edges allowed** |
    |----------------|------------|:----------------------:|:--------------------------:|
    | Graph          | Undirected | Yes                    | No                         |
    | DiGraph        | Directed   | Yes                    | No                         |
    | MultiGraph     | Undirected | Yes                    | Yes                        |
    | MultiDiGraph   | Directed   | Yes                    | Yes                        |

    See more here: [NetworkX Reference](https://networkx.org/documentation/stable/reference/classes)
    """
    Graph = nx.Graph
    DiGraph = nx.DiGraph
    MultiDiGraph = nx.MultiDiGraph
    MultiGraph = nx.MultiGraph

    @classmethod
    def of(cls, graph: nx.Graph):
        if graph.is_directed() and graph.is_multigraph():
            return cls.MultiDiGraph
        elif graph.is_directed():
            return cls.DiGraph
        elif graph.is_multigraph():
            return cls.MultiGraph
        else:
            return cls.Graph


class Builder(ABC):
    """Builder abstract base class"""

    default_node_attributes: Mapping = MappingProxyType({
        'type': 'node',
        'label': node_label_converter,
        'value': [],
        'lineage': None
    })

    default_edge_attributes: Mapping = MappingProxyType({
        'type': 'edge',
        'label': edge_label_converter,
        'value': [],
        'weight': 1.0
    })

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        self._cached_build_kwargs: dict[str, Any] = {}
        self.model = model
        self.graph_type = graph_type

    def build(self, **kwargs) -> GraphRepresentation:
        """Build a graph

        Args:
            **kwargs:

        Returns:
            Any
        """
        self._cached_build_kwargs = kwargs
        return {}


class NetworkxBuilder(Builder):
    """Build a NetworkX Graph"""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    def _initialize_graph(self):
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
    def _parent_node_id(node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
        if node_type_absolute_id[0] is UniverseNode:
            return UniverseNode

        ids = []
        for k, v in kwargs.items():
            if k[:-3] == node_type_absolute_id[1]:
                break
            ids.append(v)

        return tuple(ids)

    def _populate_nodes(self, node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
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

    def _populate_edges(self, **kwargs):
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

    def _rectify_node_attributes(self, **defaults):

        for name, default in defaults.items():
            if callable(default):
                values = {n: default(n) for n, a in self._graph.nodes(data=name, default=None) if a is None}
            elif isinstance(default, dict):
                values = default
            elif default:
                values = {n: a for n, a in self._graph.nodes(data=name, default=default) if a == default}
            else:
                values = {n: n for n, a in self._graph.nodes(data=name, default=default) if a is default}

            if values:
                nx.set_node_attributes(self._graph, values=values, name=name)

        if default_type := defaults.get('type'):
            type_count = sum(1 for n, d in self._graph.nodes(data='type') if d == default_type)
            if type_count:
                self._graph.graph['node_types'].update({default_type: type_count})

    def _rectify_edge_attributes(self, **defaults):

        for name, default in defaults.items():
            if callable(default):
                values = {tuple(e): default(tuple(e)) for *e, a in self._graph_edges(data=name, default=None)
                          if a is not None}
            elif isinstance(default, dict):
                values = default
            elif default:
                values = {tuple(e): a for *e, a in self._graph_edges(data=name, default=default) if a == default}
            else:
                values = {tuple(e): tuple(e) for *e, a in self._graph_edges(data=name, default=default) if a is default}

            if values:
                nx.set_edge_attributes(self._graph, values=values, name=name)

        if default_type := defaults.get('type'):
            type_count = sum(1 for *_, d in self._graph_edges(data='type') if d == default_type)
            if type_count:
                self._graph.graph['edge_types'].update({default_type: type_count})

    def _finalize_graph(self, **defaults):
        self._rectify_node_attributes(**defaults)

        if 'color' not in defaults:
            self._rectify_node_attributes(color=color.node_color_mapping(self._graph))

        self._rectify_edge_attributes(**self.default_edge_attributes)

        for counter_name in ('node_types', 'edge_types'):
            counter = self._graph.graph[counter_name]
            self._graph.graph[counter_name] = simplify(counter)

        self._graph.graph['created'] = utcnow()

    def build(self, **kwargs) -> GraphRepresentation:
        """

        Args:
            **kwargs:

        Returns:
            NetworkX Graph
        """
        super().build(**kwargs)
        default_node_attributes = dict(**self.default_node_attributes)
        if 'default_node_attributes' in kwargs:
            default_node_attributes.update(kwargs.pop('default_node_attributes') or {})

        default_type = default_node_attributes.get('type')
        default_label = default_node_attributes.get('label')
        self.model.rectify(_type=default_type, parent_type=default_type, label=default_label)
        self._initialize_graph()
        self._populate_node_type(**kwargs)
        self._populate_edges(**kwargs)
        self._finalize_graph(**default_node_attributes)
        return self._graph


class D3Builder(NetworkxBuilder):
    """Build a D3 Graph"""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    def build(self, values_format: Literal['json', 'python'] = 'python', **kwargs) -> GraphRepresentation:
        """

        Args:
            values_format: Literal['python', 'json'] - The format of the values
            **kwargs:

        Returns:
            D3 Graph
        """
        super().build(**kwargs)
        color.convert_colors_to_hex(self._graph)
        d3graph = self.from_networkx(self._graph)

        match values_format:
            case 'json':
                return mappingtools.transformers.strictify(d3graph, value_converter=json.dumps)
            case 'python':
                return d3graph
            case _:
                raise ValueError(f"Invalid values format: {values_format}")

    @staticmethod
    def from_networkx(nx_graph: nx.Graph):
        d3_graph = nx.node_link_data(nx_graph)
        return d3_graph


class MermaidBuilder(NetworkxBuilder):
    """Build a Mermaid Graph"""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    def build(self,
              orientation: nxm.DiagramOrientation = nxm.DiagramOrientation.LEFT_RIGHT,
              node_shape: nxm.DiagramNodeShape = nxm.DiagramNodeShape.DEFAULT,
              title: str | None = None,
              with_edge_labels: bool = False,
              **kwargs) -> nxm.typing.MermaidDiagram:
        """
        Build a Mermaid Graph

        Args:
          orientation : Orientation, optional
            The orientation of the graph, by default Orientation.LEFT_RIGHT.
          node_shape : NodeShape, optional
            The shape of the nodes, by default NodeShape.DEFAULT.
          title: str, optional
            The title of the graph (default: None).
            If None, the graph name will be used if available.
            Supplying and empty string will remove the title.
          with_edge_labels:
            Whether to include edge labels, by default False.
          **kwargs: additional inputs to the node and edge generator functions

        Returns:
            Mermaid Graph
        """
        super().build(**kwargs)
        color.convert_colors_to_hex(self._graph)
        nxm_builder = nxm.DiagramBuilder(orientation=orientation, node_shape=node_shape)
        return nxm_builder.build(self._graph, title=title, with_edge_labels=with_edge_labels)


class GraphQLBuilder(NetworkxBuilder):
    """Builds a GraphQL Schema"""

    # region - Strawberry Types

    InfNumber = strawberry.scalar(
        converters.InfNumber,
        description='Integer, Decimal or Float including Infinity and -Infinity',
        serialize=converters.infnum_to_value,
        parse_value=converters.value_to_infnum,
    )

    @strawberry.type
    class Measure:
        name: str
        value: 'GraphQLBuilder.InfNumber'

    @strawberry.interface
    class GraphElement:
        id: strawberry.ID
        type: str
        label: str
        value: Optional[list[strawberry.scalars.JSON]]
        color: Optional[str] = None
        created: Optional[datetime]
        updated: Optional[datetime]

    @strawberry.interface(description="Represents a Graph Node")
    class GraphNode(GraphElement):
        node_id: strawberry.ID
        magnitude: int
        lineage: str

        @strawberry.field()
        def neighbors(self, children: bool = False) -> list[Optional['GraphQLBuilder.GraphNode']]:
            ...  # pragma: no cover

        @strawberry.field()
        def edges(self) -> list[Optional['GraphQLBuilder.GraphEdge']]:
            ...  # pragma: no cover

    @strawberry.type(description="Represents a Graph Edge")
    class GraphEdge(GraphElement):
        source: 'GraphQLBuilder.GraphNode'
        target: 'GraphQLBuilder.GraphNode'
        weight: float

    @strawberry.type
    class Graph:
        nx_graph: strawberry.Private[nx.Graph]

        @strawberry.field()
        def radius(self) -> 'GraphQLBuilder.InfNumber':
            return nx.radius(self.nx_graph) if nx.is_connected(self.nx_graph) else math.inf

        @strawberry.field()
        def diameter(self) -> 'GraphQLBuilder.InfNumber':
            return nx.diameter(self.nx_graph) if nx.is_connected(self.nx_graph) else math.inf

        @strawberry.field()
        def name(self) -> str:
            return self.nx_graph.graph['name']

        @strawberry.field()
        def node_type_counts(self) -> list['GraphQLBuilder.Measure']:
            return [GraphQLBuilder.Measure(name=t, value=c) for t, c in self.nx_graph.graph['node_types'].items()]

        @strawberry.field()
        def edge_type_counts(self) -> list['GraphQLBuilder.Measure']:
            return [GraphQLBuilder.Measure(name=t, value=c) for t, c in self.nx_graph.graph['edge_types'].items()]

        @strawberry.field()
        def node_count(self) -> int:
            return self.nx_graph.number_of_nodes()

        @strawberry.field()
        def edge_count(self) -> int:
            return self.nx_graph.number_of_edges()

        @strawberry.field()
        def order(self) -> int:
            return self.nx_graph.order()

        @strawberry.field()
        def size(self) -> int:
            return self.nx_graph.size(weight='weight')

        # @strawberry.field()
        # def girth(self) -> int:
        #     return min(len(cycle) for cycle in nx.simple_cycles(self.graph))

        @strawberry.field()
        def average_degree(self) -> float:
            return self.nx_graph.number_of_nodes() and (
                    1.0 * sum(d for _, d in self.nx_graph.degree()) / self.nx_graph.number_of_nodes())

        @strawberry.field()
        def hash(self) -> str:
            return nx.weisfeiler_lehman_graph_hash(self.nx_graph)

        @strawberry.field()
        def created(self) -> datetime:
            return self.nx_graph.graph['created']

    @strawberry.enum(description="""
        See NetworkX documentation for explanations:
        https://networkx.org/documentation/stable/reference/index.html
        """)
    class GraphMeasure(Enum):
        is_empty = 'is_empty'
        is_directed = 'is_directed'
        is_weighted = 'is_weighted'
        is_negatively_weighted = 'is_negatively_weighted'
        is_planar = 'is_planar'
        is_regular = 'is_regular'
        is_bipartite = 'is_bipartite'
        is_chordal = 'is_chordal'
        is_eulerian = 'is_eulerian'
        is_semieulerian = 'is_semieulerian'
        has_eulerian_path = 'has_eulerian_path'
        has_bridges = 'has_bridges'
        is_asteroidal_triple_free = 'is_at_free'
        is_directed_acyclic_graph = 'is_directed_acyclic_graph'
        is_aperiodic = 'is_aperiodic'
        is_distance_regular = 'is_distance_regular'
        is_strongly_regular = 'is_strongly_regular'
        is_threshold_graph = ('networkx.algorithms.threshold', 'is_threshold_graph')
        is_connected = 'is_connected'
        is_biconnected = 'is_biconnected'
        is_strongly_connected = 'is_strongly_connected'
        is_weakly_connected = 'is_weakly_connected'
        is_semiconnected = 'is_semiconnected'
        is_attracting_component = 'is_attracting_component'
        is_tournament = ('networkx.algorithms.tournament', 'is_tournament')
        is_tree = 'is_tree'
        is_forest = 'is_forest'
        is_arborescence = 'is_arborescence'
        is_branching = 'is_branching'
        is_triad = 'is_triad'
        radius = 'radius'
        diameter = 'diameter'
        density = 'density'
        number_of_isolates = 'number_of_isolates'
        number_connected_components = 'number_connected_components'
        number_strongly_connected_components = 'number_strongly_connected_components'
        number_weakly_connected_components = ' number_weakly_connected_components'
        number_attracting_components = 'number_attracting_components'
        node_connectivity = 'node_connectivity'
        transitivity = 'transitivity'
        average_clustering = 'average_clustering'
        chordal_graph_treewidth = 'chordal_graph_treewidth'
        degree_assortativity_coefficient = 'degree_assortativity_coefficient'
        degree_pearson_correlation_coefficient = 'degree_pearson_correlation_coefficient'
        local_efficiency = 'local_efficiency'
        global_efficiency = 'global_efficiency'
        flow_hierarchy = 'flow_hierarchy'
        average_shortest_path_length = 'average_shortest_path_length'
        overall_reciprocity = 'overall_reciprocity'
        wiener_index = 'wiener_index'

    # endregion - Strawberry Types

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    @staticmethod
    def add_field_resolver(class_dict: dict, field_name: str, resolver: Callable, graphql_type: Optional[Any] = None):
        class_dict[field_name] = strawberry.field(resolver=resolver, graphql_type=graphql_type)
        class_dict['__annotations__'][field_name] = inspect.getfullargspec(resolver).annotations['return']

    @staticmethod
    def _graph_node(node_class: type['GraphQLBuilder.GraphNode'],
                    node: tuple,
                    node_data: dict) -> 'GraphQLBuilder.GraphNode':
        kwargs = {
            'id': encode_id(node),
            'node_id': str(node),
            'type': node_data['type'],
            'label': node_data.get('label', node_label_converter(node)),
            'value': [json.dumps(v, default=str) for v in node_data['value']],
            'magnitude': node_data.get('magnitude', 1),
            'lineage': str(node_data['lineage']),
            'color': color.color_hex(node_data['color']),
            'created': node_data.get('created'),
            'updated': node_data.get('updated')
        }

        return node_class(**kwargs)

    def _graph_edge(self, edge: tuple, edge_data: dict):
        graphql_types = self._graphql_types
        nodes_with_data = ((n, self._graph.nodes[n]) for n in edge)
        nodes_args = ((graphql_types.get(d.get('type'), ), n, d) for n, d in nodes_with_data)
        source, target = tuple(self._graph_node(*args) for args in nodes_args)

        return GraphQLBuilder.GraphEdge(
            id=encode_edge_id(edge),
            source=source,
            target=target,
            type=edge_data.get('type', ''),
            label=edge_data.get('label', edge_label_converter(edge)),
            value=[json.dumps(v, default=str) for v in edge_data['value']],
            weight=edge_data.get('weight', 1.0),
            color=color.color_hex(edge_data.get('color')),
            created=edge_data.get('created'),
            updated=edge_data.get('updated')
        )

    @staticmethod
    def _graphql_type(name: str, type_class: type['GraphQLBuilder.GraphNode']) -> type['GraphQLBuilder.GraphNode']:
        capitalized_name = name.capitalize()
        return strawberry.type(
            type_class,
            name=f"{capitalized_name}{'' if name.lower().endswith('node') else 'Node'}",
            description=f"Represents a {capitalized_name} Graph Node"
        )

    @classmethod
    @functools.lru_cache
    def _children_types(cls, model: GraphModel, node_type: str):
        return model.node_children_types(node_type).get(node_type, [])

    @property
    @functools.lru_cache
    def _graphql_types(self) -> dict[str, type['GraphQLBuilder.GraphNode']]:
        node_types = list(self._graph.graph['node_types'].keys())

        def neighbors_resolver():
            graph = self._graph

            children_types = set(self._children_types(self.model, node_type))

            def node_neighbors(self, children: bool = False) -> list[Optional[GraphQLBuilder.GraphNode]]:
                node = decode_id(self.id)
                items = (GraphQLBuilder._graph_node(graphql_types[d['type']], n, d) for n, d in graph.nodes(data=True)
                         if n in graph.neighbors(node))

                if children and children_types:
                    return [item for item in items if item.type in children_types]

                return list(items)

            return node_neighbors

        def edges_resolver():
            graph: nx.Graph = self._graph
            graph_edge = self._graph_edge

            def node_edges(self) -> list[Optional[GraphQLBuilder.GraphEdge]]:
                node = decode_id(self.id)
                return [graph_edge((source, target), data) for source, target, data in graph.edges(node, data=True)]

            return node_edges

        # Create classes for nodes according to their type
        graphql_types: dict[str, type[GraphQLBuilder.GraphNode]] = {}
        for node_type in node_types:
            class_name = node_type.capitalize()
            bases = (GraphQLBuilder.GraphNode,)
            class_dict = {
                '__doc__': f"A {class_name} Graph Node",
                '__annotations__': {}
            }

            self.add_field_resolver(class_dict, 'neighbors', neighbors_resolver())
            self.add_field_resolver(class_dict, 'edges', edges_resolver())

            # noinspection PyTypeChecker
            graphql_type: type[GraphQLBuilder.GraphNode] = type(class_name, bases, class_dict)
            graphql_types[node_type] = GraphQLBuilder._graphql_type(node_type, graphql_type)

        return graphql_types

    def _graphql_query(self):  # noqa: C901
        # inflect engine to generate Plurals when needed
        inflection = inflect.engine()

        # local reference to instance fields used to "inject" into dynamically generated class methods
        def get_graph():
            return self._graph

        graphql_types = self._graphql_types

        # region - Defining GraphQL Query Class dict
        query_class_dict = {'__annotations__': {}}

        # region - Defining GraphQL Query Class dict - graph field
        def graphql_graph(self) -> GraphQLBuilder.Graph:
            return GraphQLBuilder.Graph(nx_graph=get_graph())

        self.add_field_resolver(query_class_dict, 'graph', graphql_graph)

        # endregion

        # region - Defining GraphQL Query Class dict - nodes field
        def graph_nodes_resolver(
                graphql_type: Optional[type[GraphQLBuilder.GraphNode]] = None,
                node_type: Optional[str] = None
        ) -> Callable[[Optional[strawberry.ID]], list[GraphQLBuilder.GraphNode]]:

            def graph_nodes(self,
                            node_id: Optional[strawberry.ID] = strawberry.UNSET) -> list[GraphQLBuilder.GraphNode]:

                decoded_node_id = node_id and decode_id(node_id)

                graph = get_graph()

                if graphql_type:
                    nodes = (GraphQLBuilder._graph_node(graphql_type, n, d)
                             for n, d in graph.nodes(data=True))
                else:
                    nodes = (GraphQLBuilder._graph_node(graphql_types.get(d['type']), n, d)
                             for n, d in graph.nodes(data=True))

                def filter_node(node):
                    output = True
                    if node_type:
                        output = node.type.lower() == node_type

                    if decoded_node_id:
                        output = output and (decode_id(node.id) == decoded_node_id)

                    return output

                items = [node for node in nodes if filter_node(node)]

                return items

            return graph_nodes

        self.add_field_resolver(query_class_dict, 'nodes', graph_nodes_resolver())

        # endregion

        # region - Defining GraphQL Query Class dict - edges field
        def graph_edges_resolver() -> Callable[[Optional[strawberry.ID]], list[GraphQLBuilder.GraphEdge]]:

            graph_edge = self._graph_edge

            def graph_edges(self,
                            edge_id: Optional[strawberry.ID] = strawberry.UNSET) -> list[GraphQLBuilder.GraphEdge]:
                decoded_edge_id = edge_id and decode_edge_id(edge_id)

                graph = get_graph()

                edges = (graph_edge((source, target), data) for source, target, data in graph.edges(data=True))

                def filter_edge(edge):
                    output = True
                    if decoded_edge_id:
                        output = decode_edge_id(edge.id) == decoded_edge_id

                    return output

                return [edge for edge in edges if filter_edge(edge)]

            return graph_edges

        self.add_field_resolver(query_class_dict, 'edges', graph_edges_resolver())
        # endregion

        # region - Defining GraphQL Query Class dict - fields for GraphQL types implementing 'GraphNode' interface
        for node_type, graphql_type in self._graphql_types.items():
            field_name = inflection.plural(node_type)
            resolver = graph_nodes_resolver(graphql_type, node_type)
            self.add_field_resolver(query_class_dict, field_name, resolver)

        # endregion

        # region - Defining GraphQL Query Class dict - field measure for 'GraphMeasure' GraphQL type

        def graph_measure(self, measure: GraphQLBuilder.GraphMeasure) -> GraphQLBuilder.Measure:

            graph = get_graph()

            if isinstance(measure.value, str):
                method = measure.value
                module = nx
            else:
                method = measure.value[1]
                module = importlib.import_module(measure.value[0])

            value_getter = operator.attrgetter(method)(module)
            value = float(value_getter(graph))
            return GraphQLBuilder.Measure(name=measure.name, value=value)

        # query_class_dict['measure'] = strawberry.field(resolver=graph_measure)
        # query_class_dict['__annotations__']['measure'] = float
        self.add_field_resolver(query_class_dict, 'measure', graph_measure)
        # endregion

        # region - Defining GraphQL Query Class dict - create Query Class and Query Type
        query_class = type('Query', (), query_class_dict)
        query_graphql_type = strawberry.type(query_class, name='Query')
        # endregion

        # endregion - Defining GraphQL Query Class dict

        return query_graphql_type

    def _graphql_mutation(self):

        refresh_graph = functools.partial(super().build, **self._cached_build_kwargs)

        @strawberry.type
        class Mutation:

            @strawberry.mutation
            def refresh(self) -> bool:
                refresh_graph()
                return True

        return Mutation

    def schema(self) -> strawberry.Schema:
        # define and return Schema
        return strawberry.Schema(
            query=self._graphql_query(),
            mutation=self._graphql_mutation(),
            types=self._graphql_types.values(),
            extensions=[
                ParserCache(maxsize=100),
                QueryDepthLimiter(max_depth=10),
                ValidationCache(maxsize=100)
            ]
        )

    def build(self, **kwargs) -> GraphRepresentation:
        """

        Args:
            **kwargs:

        Returns:
            Strawberry GraphQL Schema
        """
        super().build(**kwargs)
        return self.schema()


def build(builder_cls: type[Builder],
          graph_model: GraphModel,
          graph_type: GraphType = GraphType.Graph,
          default_node_attributes: Optional[Mapping] = None,
          **kwargs) -> Any:
    """
    Build a graph from a graph model

    Args:
        builder_cls: builder class type
        graph_model: a GraphModel instance
        graph_type: type of the generated graph
        default_node_attributes: default node attributes
        **kwargs: node id values

    Returns:
         Graph data structure
    """

    builder = builder_cls(graph_model, graph_type)
    materialized_graph = builder.build(default_node_attributes=default_node_attributes, **kwargs)
    return materialized_graph


__all__ = ('D3Builder', 'GraphQLBuilder', 'GraphRepresentation', 'GraphType', 'NetworkxBuilder', 'build')
