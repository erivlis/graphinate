"""
Build classes that can generate graph data structures from a GraphModel
"""

import base64
import decimal
import functools
import gzip
import importlib
import inspect
import json
import math
import operator
import pickle
from abc import ABC
from collections import Counter
from collections.abc import Hashable, Iterable, Mapping
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Callable, NewType, Optional, Union

import inflect
import networkx as nx
import strawberry
from loguru import logger

from . import color
from .modeling import GraphModel, UNIVERSE_NODE
from .tools import mutators
from .typing import NodeTypeAbsoluteId

DEFAULT_NODE_DELIMITER = ' ∋ '
DEFAULT_EDGE_DELIMITER = ' ↔ '


def label_converter(value, delimiter: str):
    if value:
        return delimiter.join(str(v) for v in value) if isinstance(value, tuple) else str(value)

    return value


node_label_converter = functools.partial(label_converter, delimiter=DEFAULT_NODE_DELIMITER)


def edge_label_converter(value):
    return label_converter(tuple(node_label_converter(n) for n in value), delimiter=DEFAULT_EDGE_DELIMITER)


def encode_id(graph_node_id: tuple,
              encoding: str = 'utf-8',
              delimiter: str = DEFAULT_NODE_DELIMITER) -> str:
    # obj_s: str = delimiter.join(graph_node_id)
    # obj_b: bytes = obj_s.encode(encoding)
    obj_b = gzip.compress(pickle.dumps(graph_node_id))
    enc_b: bytes = base64.b64encode(obj_b)
    enc_s: str = enc_b.decode(encoding)

    return enc_s


def decode_id(graphql_node_id: strawberry.ID,
              encoding: str = 'utf-8',
              delimiter: str = DEFAULT_NODE_DELIMITER) -> tuple[str, ...]:
    enc_b: bytes = graphql_node_id.encode(encoding)
    obj_b: bytes = base64.b64decode(enc_b)
    # noinspection PickleLoad
    obj = pickle.loads(gzip.decompress(obj_b))
    # obj_s: str = obj_b.decode(encoding)
    # obj: tuple = tuple(obj_s.split(delimiter))
    return obj


def encode_edge_id(edge: tuple, encoding: str = 'utf-8'):
    encoded_edge = tuple(encode_id(n, encoding) for n in edge)
    return encode_id(encoded_edge, encoding)


def decode_edge_id(graphql_edge_id: strawberry.ID, encoding: str = 'utf-8'):
    encoded_edge: tuple = decode_id(graphql_edge_id, encoding)
    return tuple(decode_id(enc_node) for enc_node in encoded_edge)


class GraphType(Enum):
    """Graph Types `1`_

    .. _1:
        https://networkx.org/documentation/stable/reference/classes/index.html
    """
    Graph = nx.Graph
    DiGraph = nx.DiGraph
    MultiDiGraph = nx.MultiDiGraph
    MultiGraph = nx.MultiGraph


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
        self._cached_build_kwargs = {}
        self.model = model
        self.graph_type = graph_type

    def build(self, **kwargs):
        """build a graph"""
        self._cached_build_kwargs = kwargs


class NetworkxBuilder(Builder):
    """Build a NetworkX Graph"""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    def _initialize_graph(self):
        self._graph = self.graph_type.value(name=self.model.name,
                                            node_types=Counter(),
                                            edge_types=Counter())

    def _populate_node_type(self, node_type: Union[Hashable, UNIVERSE_NODE] = UNIVERSE_NODE, **kwargs):
        for parent_node_type, child_node_types in self.model.node_children_types(node_type).items():
            for child_node_type in child_node_types:
                node_type_absolute_id = (parent_node_type, child_node_type)
                self._populate_nodes(node_type_absolute_id, **kwargs)

    @staticmethod
    def _parent_node_id(node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
        if node_type_absolute_id[0] is UNIVERSE_NODE:
            return UNIVERSE_NODE

        ids = []
        for k, v in kwargs.items():
            if k[:-3] == node_type_absolute_id[1]:
                break
            ids.append(v)
        return tuple(ids)

        # return (*(kwargs.values()),) if kwargs else UNIVERSE_NODE

    def _populate_nodes(self, node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
        node_model = self.model.node_models[node_type_absolute_id]
        unique = node_model.uniqueness
        for node in node_model.generator(**kwargs):
            parent_node_id = self._parent_node_id(node_type_absolute_id, **kwargs)
            node_lineage = (*parent_node_id, node.key) if parent_node_id is not UNIVERSE_NODE else (node.key,)
            node_id = (node.key,) if unique else node_lineage

            label = node.key
            if node_model.label is not None:
                label = node_model.label(node.value) if callable(node_model.label) else node_model.label

            node_type = node.__class__.__name__.lower()
            if node_type == 'tuple':
                node_type = node_model.type.lower()

            logger.debug("Adding node: '{}'", node_id)

            if node_id in self._graph:
                self._graph.nodes[node_id]['value'].append(node.value)
                self._graph.nodes[node_id]['magnitude'] += 1
                self._graph.nodes[node_id]['updated'] = datetime.utcnow()
            else:
                self._graph.add_node(node_id,
                                     label=label,
                                     type=node_type,
                                     value=[node.value],
                                     magnitude=1,
                                     lineage=list(node_lineage),
                                     created=datetime.utcnow())

                self._graph.graph['node_types'].update({node_type: 1})

            if node_model.parent_type is not UNIVERSE_NODE:
                logger.debug("Adding edge from: '{}' to '{}'", parent_node_id, node_id)
                self._graph.add_edge(parent_node_id,
                                     node_id,
                                     created=datetime.utcnow())

            new_kwargs = kwargs.copy()
            new_kwargs[f"{node_type}_id"] = node.key
            self._populate_node_type(node_model.type, **new_kwargs)

    def _populate_edges(self, **kwargs):
        for edge_type, edge_generators in self.model.edge_generators.items():
            for edge_generator in edge_generators:
                for edge in edge_generator(**kwargs):
                    edge_id = ((edge.source,), (edge.target,))
                    edge_weight = edge.weight or 1.0
                    logger.debug("Adding edge from: '{}' to: '{}'", edge.source, edge.target)

                    if isinstance(self._graph, nx.MultiGraph) or edge_id not in self._graph.edges:
                        self._graph.add_edge((edge.source,),
                                             (edge.target,),
                                             label=edge.label,
                                             type=edge_type,
                                             value=[edge.value],
                                             weight=edge_weight,
                                             created=datetime.utcnow())
                        self._graph.graph['edge_types'].update({edge_type: 1})
                    else:
                        self._graph.edges[edge_id]['value'].append(edge.value)
                        self._graph.edges[edge_id]['weight'] += edge_weight
                        self._graph.edges[edge_id]['updated'] = datetime.utcnow()

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
                values = {(s, t): default((s, t)) for s, t, a in self._graph.edges(data=name, default=None) if
                          a is None}
            elif isinstance(default, dict):
                values = default
            elif default:
                values = {(s, t): a for s, t, a in self._graph.edges(data=name, default=default) if a == default}
            else:
                values = {(s, t): (s, t) for s, t, a in self._graph.edges(data=name, default=default) if a is default}

            if values:
                nx.set_edge_attributes(self._graph, values=values, name=name)

        if default_type := defaults.get('type'):
            type_count = sum(1 for s, t, d in self._graph.edges(data='type') if d == default_type)
            if type_count:
                self._graph.graph['edge_types'].update({default_type: type_count})

    def _finalize_graph(self, **defaults):
        self._rectify_node_attributes(**defaults)

        if 'color' not in defaults:
            self._rectify_node_attributes(color=color.node_color_mapping(self._graph))

        self._rectify_edge_attributes(**self.default_edge_attributes)

        for counter_name in ('node_types', 'edge_types'):
            counter = self._graph.graph[counter_name]
            self._graph.graph[counter_name] = mutators.dictify(counter)

        self._graph.graph['created'] = datetime.utcnow()

    def build(self, **kwargs):
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

    def build(self, **kwargs) -> dict:
        super().build(**kwargs)
        return self.from_networkx(self._graph)

    @staticmethod
    def from_networkx(nx_graph: nx.Graph):
        d3_graph = nx.node_link_data(nx_graph)
        return d3_graph


class GraphQLBuilder(NetworkxBuilder):
    """Builds a GraphQL Schema"""

    # region Strawberry Types

    InfNumber = strawberry.scalar(
        NewType("InfInt", Union[float, int, decimal.Decimal]),
        serialize=lambda v: 'Infinity' if v == math.inf else ('-Infinity' if v == -math.inf else v),
        parse_value=lambda v: math.inf if v == 'Infinity' else (-math.inf if v == '-Infinity' else v),
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
        neighbors: Optional[list['GraphQLBuilder.GraphNode']]

    @strawberry.type(description="Represents a Graph Edge")
    class GraphEdge(GraphElement):
        source: 'GraphQLBuilder.GraphNode'
        target: 'GraphQLBuilder.GraphNode'
        weight: float

    @strawberry.type
    class Graph:
        graph: strawberry.Private[nx.Graph]

        name: str
        created: datetime
        hash: str
        node_type_counts: list['GraphQLBuilder.Measure']
        edge_type_counts: list['GraphQLBuilder.Measure']
        node_count: int
        edge_count: int
        order: int
        size: int
        # girth: int
        average_degree: float

        @strawberry.field()
        def radius(self) -> 'GraphQLBuilder.InfNumber':
            return nx.radius(self.graph, weight='weight') if nx.is_connected(self.graph) else math.inf

        @strawberry.field()
        def diameter(self) -> 'GraphQLBuilder.InfNumber':
            return nx.diameter(self.graph, weight='weight') if nx.is_connected(self.graph) else math.inf

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

    # endregion Strawberry Types

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    @staticmethod
    def add_field_resolver(class_dict: dict, field_name: str, resolver: Callable):
        class_dict[field_name] = strawberry.field(resolver=resolver)
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
        # node_types = self.model.node_types
        node_types = list(self._graph.graph['node_types'].keys())

        # Create classes for nodes according to their type
        graphql_types: dict[str, type[GraphQLBuilder.GraphNode]] = {}
        for node_type in node_types:
            class_name = node_type.capitalize()
            bases = (GraphQLBuilder.GraphNode,)
            class_dict = {
                '__doc__': f"A {class_name} Graph Node",
            }
            # noinspection PyTypeChecker
            graphql_type: type[GraphQLBuilder.GraphNode] = type(class_name, bases, class_dict)
            graphql_types[node_type] = graphql_type

        def neighbors_resolver(neighbors_types: Optional[Iterable[str]] = None):
            graph = self._graph

            def neighbors(self, children: bool = False) -> list[GraphQLBuilder.GraphNode]:
                node = decode_id(self.id)
                items = (GraphQLBuilder._graph_node(graphql_types[d['type']], n, d) for n, d in graph.nodes(data=True)
                         if n in graph.neighbors(node))

                if children and neighbors_types:
                    return [item for item in items if item.type in neighbors_types]

                return list(items)

            return neighbors

        # node_types = self.model.node_types
        for node_type in node_types:
            graphql_types[node_type].neighbors = strawberry.field(resolver=neighbors_resolver())
            # children_types = set(self._children_types(node_type))
            # graphql_types[node_type].children = strawberry.field(resolver=neighbors_resolver(children_types))

        return {k: GraphQLBuilder._graphql_type(k, v) for k, v in graphql_types.items()}

    def _graphql_query(self):  # noqa: C901
        # inflect engine to generate Plurals when needed
        inflection = inflect.engine()

        # local reference to instance fields in order to "inject" into dynamically generated class methods
        def get_graph():
            return self._graph

        graphql_types = self._graphql_types

        # region - Defining GraphQL Query Class dict
        query_class_dict = {'__annotations__': {}}

        # region - Defining GraphQL Query Class dict - graph field
        def graphql_graph(self) -> GraphQLBuilder.Graph:
            graph = get_graph()
            return GraphQLBuilder.Graph(
                graph=graph,
                name=graph.graph['name'],
                node_type_counts=[GraphQLBuilder.Measure(name=t, value=c) for t, c in
                                  graph.graph['node_types'].items()],
                edge_type_counts=[GraphQLBuilder.Measure(name=t, value=c) for t, c in
                                  graph.graph['edge_types'].items()],
                node_count=graph.number_of_nodes(),
                edge_count=graph.number_of_edges(),
                order=graph.order(),
                size=graph.size(weight='weight'),
                # girth=min(len(cycle) for cycle in nx.simple_cycles(graph)),
                average_degree=graph.number_of_nodes() and (
                        1.0 * sum(d for _, d in graph.degree()) / graph.number_of_nodes()),
                hash=nx.weisfeiler_lehman_graph_hash(graph),
                created=graph.graph['created'],
            )

        self.add_field_resolver(query_class_dict, 'graph', graphql_graph)

        # endregion

        # region - Defining GraphQL Query Class dict - nodes field
        def graph_nodes_resolver(
                graphql_type: Optional[type[GraphQLBuilder.GraphNode]] = None,
                node_type: Optional[str] = None
        ) -> Callable[[Optional[strawberry.ID]], list[GraphQLBuilder.GraphNode]]:

            def graph_nodes(self,
                            node_id: Optional[strawberry.ID] = strawberry.UNSET) -> list[GraphQLBuilder.GraphNode]:

                graph = get_graph()

                if graphql_type:
                    nodes = (GraphQLBuilder._graph_node(graphql_type, n, d) for n, d in graph.nodes(data=True))
                else:
                    nodes = (GraphQLBuilder._graph_node(graphql_types.get(d['type']), n, d) for n, d in
                             graph.nodes(data=True))

                def filter_node(node):
                    output = True
                    if node_type:
                        output = output and node.type.lower() == node_type

                    if node_id:
                        output = output and node.id == node_id

                    return output

                return [node for node in nodes if filter_node(node)]

            return graph_nodes

        self.add_field_resolver(query_class_dict, 'nodes', graph_nodes_resolver())

        # endregion

        # region - Defining GraphQL Query Class dict - edges field
        def graph_edges_resolver() -> Callable[[Optional[strawberry.ID]], list[GraphQLBuilder.GraphEdge]]:

            graph_edge = self._graph_edge

            def graph_edges(self,
                            edge_id: Optional[strawberry.ID] = strawberry.UNSET) -> list[GraphQLBuilder.GraphEdge]:
                graph = get_graph()

                edges = (graph_edge((source, target), data) for source, target, data in graph.edges(data=True))

                def filter_edge(edge):
                    output = True
                    if edge_id:
                        output = edge.id == edge_id

                    return output

                return [edge for edge in edges if filter_edge(edge)]

            return graph_edges

        self.add_field_resolver(query_class_dict, 'edges', graph_edges_resolver())
        # endregion

        # region  - Defining GraphQL Query Class dict - fields for GraphQL types implementing 'GraphNode' interface
        for node_type, graphql_type in self._graphql_types.items():
            field_name = inflection.plural(node_type)
            resolver = graph_nodes_resolver(graphql_type, node_type)
            self.add_field_resolver(query_class_dict, field_name, resolver)

        # endregion

        #  region  - Defining GraphQL Query Class dict - field measure for 'GraphMeasure' GraphQL type

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
        return strawberry.Schema(query=self._graphql_query(),
                                 mutation=self._graphql_mutation(),
                                 types=self._graphql_types.values())

    def build(self, **kwargs) -> strawberry.Schema:
        super().build(**kwargs)
        return self.schema()


def build(builder_cls: type[Builder],
          graph_model: GraphModel,
          graph_type: GraphType = GraphType.Graph,
          default_node_attributes: Optional[Mapping] = None,
          **kwargs):
    """
    Build a graph from a graph model

    Parameters:
        builder_cls: builder class type
        graph_model: a GraphModel instance
        graph_type: type on output graph
        default_node_attributes: default node attributes
        kwargs: node id values

    Returns:
         Graph data structure
    """

    builder = builder_cls(graph_model, graph_type)
    materialized_graph = builder.build(default_node_attributes=default_node_attributes, **kwargs)
    return materialized_graph
