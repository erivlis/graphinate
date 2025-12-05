import functools
import importlib
import inspect
import json
import math
import operator
from collections.abc import Callable
from datetime import datetime
from enum import Enum, EnumType
from typing import Any, Optional

import inflect
import networkx as nx
import strawberry
from strawberry.extensions import ParserCache, QueryDepthLimiter, ValidationCache
from strawberry.types.base import StrawberryType

from .. import color, converters
from ..converters import (
    decode_edge_id,
    decode_id,
    edge_label_converter,
    encode_edge_id,
    encode_id,
    node_label_converter,
)
from ..enums import GraphType
from ..modeling import GraphModel
from ._networkx import NetworkxBuilder


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
        value: list[strawberry.scalars.JSON] | None
        color: str | None = None
        created: datetime | None
        updated: datetime | None

    @strawberry.enum
    class GraphNodeType(Enum):
        ...  # pragma: no cover

    @strawberry.interface(description="Represents a Graph Node")
    class GraphNode(GraphElement):
        node_id: strawberry.ID
        magnitude: int
        lineage: str

        @strawberry.field()
        def neighbors(self,
                      type: 'GraphQLBuilder.GraphNodeType | None' = None,
                      children: bool = False) -> list[Optional['GraphQLBuilder.GraphNode']]:
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
        self._node_value_graphql_type_supplier: Callable[[str], StrawberryType | None] | None = None

    @staticmethod
    def add_field_resolver(class_dict: dict, field_name: str, resolver: Callable, graphql_type: Any | None = None):
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
            'value': node_data['value'],
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

    @staticmethod
    def _graphql_enum(name: str, values: list[str]) -> EnumType:
        return strawberry.enum(
            Enum(name, {v: v for v in values}),
            name=name,
            description=f"{name} Enumeration"
        )

    @classmethod
    @functools.lru_cache
    def _children_types(cls, model: GraphModel, node_type: str):
        return model.node_children_types(node_type).get(node_type, [])

    def _populate_graph_node_type_enum(self, node_types: list[str]):
        from strawberry.types.enum import EnumValue

        for v in node_types:
            self.GraphNodeType._member_names_.append(v)
            self.GraphNodeType._member_map_[v] = v
            self.GraphNodeType._value2member_map_[v] = v

            self.GraphNodeType.__strawberry_definition__.values.append(
                EnumValue(
                    name=v,
                    value=v,
                    description=f"Graph Node Type: {v}"
                )
            )

    @property
    @functools.lru_cache
    def _graphql_types(self) -> dict[str, type['GraphQLBuilder.GraphNode']]:
        node_types = list(self._graph.graph['node_types'].keys())

        self._populate_graph_node_type_enum(node_types)

        def neighbors_resolver():
            graph = self._graph

            children_types = set(self._children_types(self.model, node_type))

            def node_neighbors(self,
                               type: 'GraphQLBuilder.GraphNodeType | None' = None,
                               children: bool = False) -> list['GraphQLBuilder.GraphNode']:
                node = decode_id(self.id)
                items = (GraphQLBuilder._graph_node(graphql_types[d['type']], n, d)
                         for n, d in graph.nodes(data=True)
                         if n in graph.neighbors(node))

                if type is not None:
                    items = (item for item in items if item.type == type)

                if children and children_types:
                    items = (item for item in items if item.type in children_types)

                items = list(items)
                return items

            return node_neighbors

        def edges_resolver():
            graph: nx.Graph = self._graph
            graph_edge = self._graph_edge

            def node_edges(self) -> list[GraphQLBuilder.GraphEdge | None]:
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

            if (
                    self._node_value_graphql_type_supplier is not None
                    and (value_graphql_type := self._node_value_graphql_type_supplier(node_type) is not None)
            ):
                class_dict['value'] = list[value_graphql_type]

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
                graphql_type: type[GraphQLBuilder.GraphNode] | None = None,
                node_type: str | None = None
        ) -> Callable[[strawberry.ID | None], list[GraphQLBuilder.GraphNode]]:

            def graph_nodes(self,
                            node_id: strawberry.ID | None = strawberry.UNSET) -> list[GraphQLBuilder.GraphNode]:

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
        def graph_edges_resolver() -> Callable[[strawberry.ID | None], list[GraphQLBuilder.GraphEdge]]:

            graph_edge = self._graph_edge

            def graph_edges(self,
                            edge_id: strawberry.ID | None = strawberry.UNSET) -> list[GraphQLBuilder.GraphEdge]:
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

    def build(self,
              node_value_graphql_type_supplier: Callable[[str], StrawberryType | None] | None = None,
              **kwargs: Any) -> strawberry.Schema:
        """

        Args:
            node_value_graphql_type_supplier: Callable[[str], StrawberryType]]
            **kwargs:

        Returns:
            Strawberry GraphQL Schema
        """
        super().build(**kwargs)

        self._node_value_graphql_type_supplier = node_value_graphql_type_supplier

        return self.schema()
