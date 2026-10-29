import functools
import importlib
import inspect
import json
import math
import operator
import types
from collections.abc import Callable, Mapping
from datetime import datetime
from enum import Enum
from enum import EnumMeta as EnumType  # support Python 3.10
from typing import Any, NewType, Optional

import inflect
import networkx as nx
import strawberry
from strawberry.extensions import ParserCache, QueryDepthLimiter, ValidationCache
from strawberry.schema.config import StrawberryConfig
from strawberry.tools import create_type
from strawberry.types import Info
from strawberry.types.base import StrawberryType

from .. import color, converters
from ..converters import (
    decode_edge_id,
    decode_node_id,
    edge_label_converter,
    encode_edge_id,
    encode_node_id,
    node_label_converter,
)
from ..enums import DynamicFieldNaming, GraphType, SchemaMode
from ..modeling import GraphModel
from ..tools import VariableNameManager
from .networkx import NetworkxBuilder


class GraphQLBuilder(NetworkxBuilder):
    """Builds a GraphQL Schema"""

    # region - Strawberry Types

    InfNumber = NewType('InfNumber', object)

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

    @strawberry.type(description="Represents a Generic Graph Node")
    class GenericGraphNode(GraphNode):
        """Static generic GraphNode implementation used in SchemaMode.STATIC."""

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
        number_weakly_connected_components = 'number_weakly_connected_components'
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

    def __init__(
        self,
        model: GraphModel,
        graph_type: GraphType = GraphType.Graph,
        mode: SchemaMode = SchemaMode.DYNAMIC,
        dynamic_field_naming: DynamicFieldNaming = DynamicFieldNaming.EXPLICIT,
    ):
        super().__init__(model, graph_type)
        self.mode: SchemaMode = mode
        try:
            self.dynamic_field_naming = DynamicFieldNaming(dynamic_field_naming)
        except ValueError:
            raise ValueError(
                f"Invalid dynamic_field_naming: '{dynamic_field_naming}'. "
                f"Expected one of: {list(DynamicFieldNaming)}."
            ) from None
        self._node_value_graphql_type_supplier: Callable[[str], StrawberryType | None] | None = None
        self._cached_graphql_types: dict[str, type[GraphQLBuilder.GraphNode]] | None = None

    def _resolve_graph(self, info: Info | None = None) -> nx.Graph:
        """Resolve the NetworkX graph from the GraphQL execution context if present, else fallback to self._graph."""
        if info is not None and isinstance(info.context, Mapping) and 'graph' in info.context:
            return info.context['graph']
        return self._graph

    @staticmethod
    def add_field_resolver(class_dict: dict, field_name: str, resolver: Callable, graphql_type: Any | None = None):
        class_dict[field_name] = strawberry.field(resolver=resolver, graphql_type=graphql_type)
        class_dict['__annotations__'][field_name] = inspect.getfullargspec(resolver).annotations['return']

    @staticmethod
    def _graph_node(node_class: type['GraphQLBuilder.GraphNode'],
                    node: tuple,
                    node_data: dict) -> 'GraphQLBuilder.GraphNode':
        kwargs = {
            'id': encode_node_id(node),
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

    def _resolve_node_class(self, node_type: str) -> type['GraphQLBuilder.GraphNode']:
        if self.mode == SchemaMode.STATIC:
            return self._graphql_types.get('node', GraphQLBuilder.GenericGraphNode)
        return self._graphql_types.get(node_type, GraphQLBuilder.GenericGraphNode)

    def _graph_edge(self, edge: tuple, edge_data: dict, graph: nx.Graph | None = None):
        active_graph = self._graph if graph is None else graph
        nodes_with_data = ((n, active_graph.nodes[n]) for n in edge)
        nodes_args = ((self._resolve_node_class(d.get('type')), n, d) for n, d in nodes_with_data)
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
        name_manager = VariableNameManager()
        return strawberry.enum(
            Enum(name, {name_manager.make_valid(v): v for v in values}),
            name=name,
            description=f"{name} Enumeration"
        )

    @classmethod
    @functools.lru_cache
    def _children_types(cls, model: GraphModel, node_type: str):
        return model.node_children_types(node_type).get(node_type, [])

    def _populate_graph_node_type_enum(self, node_types: list[str]):
        from strawberry.types.enum import EnumValue

        types_to_populate = node_types if node_types else ['node']
        name_manager = VariableNameManager()

        self.GraphNodeType.__strawberry_definition__.values.clear()

        for v in types_to_populate:
            member_name = name_manager.make_valid(v)
            if member_name not in self.GraphNodeType._member_names_:
                self.GraphNodeType._member_names_.append(member_name)
            self.GraphNodeType._member_map_[member_name] = v
            self.GraphNodeType._value2member_map_[v] = v

            self.GraphNodeType.__strawberry_definition__.values.append(
                EnumValue(
                    name=member_name,
                    value=v,
                    description=f"Graph Node Type: {v}"
                )
            )

    def _make_neighbors_resolver(self, current_node_type: str | None = None):
        builder = self

        def node_neighbors(
                root: GraphQLBuilder.GraphNode,
                info: Info,
                type: 'GraphQLBuilder.GraphNodeType | None' = None,
                children: bool = False,
        ) -> list['GraphQLBuilder.GraphNode']:
            graph = builder._resolve_graph(info)
            node = decode_node_id(root.id)
            effective_type = current_node_type or root.type
            children_types = set(builder._children_types(builder.model, effective_type))

            items = (
                GraphQLBuilder._graph_node(builder._resolve_node_class((d := graph.nodes[n])['type']), n, d)
                for n in graph.neighbors(node)
            )

            if type is not None:
                target_type = getattr(type, 'value', type)
                items = (item for item in items if item.type == target_type)

            if children and children_types:
                items = (item for item in items if item.type in children_types)

            return list(items)

        return node_neighbors

    def _make_edges_resolver(self):
        builder = self

        def node_edges(root: GraphQLBuilder.GraphNode, info: Info) -> list[GraphQLBuilder.GraphEdge | None]:
            graph = builder._resolve_graph(info)
            node = decode_node_id(root.id)
            return [
                builder._graph_edge((source, target), data, graph=graph)
                for source, target, data in graph.edges(node, data=True)
            ]

        return node_edges

    @staticmethod
    def _create_node_type(
            name: str,
            fields: list[Any],
            description: str,
    ) -> type['GraphQLBuilder.GraphNode']:
        namespace: dict[str, Any] = {}
        annotations: dict[str, Any] = {}
        for field in fields:
            field_name = field.graphql_name or field.python_name
            field.python_name = field_name
            namespace[field_name] = field
            annotations[field_name] = field.type
        namespace['__annotations__'] = annotations
        cls = types.new_class(name, (GraphQLBuilder.GraphNode,), {}, lambda ns: ns.update(namespace))
        return strawberry.type(cls, name=name, description=description)

    @property
    def _graphql_types(self) -> dict[str, type['GraphQLBuilder.GraphNode']]:
        if self._cached_graphql_types is not None:
            return self._cached_graphql_types

        node_types = list(self._graph.graph['node_types'].keys())
        self._populate_graph_node_type_enum(node_types)

        if self.mode == SchemaMode.STATIC:
            static_fields = [
                strawberry.field(name='neighbors', resolver=self._make_neighbors_resolver(None)),
                strawberry.field(name='edges', resolver=self._make_edges_resolver()),
            ]
            static_type = self._create_node_type(
                name='GenericGraphNode',
                fields=static_fields,
                description='Represents a Generic Graph Node',
            )
            graphql_types = {'node': static_type}
            for nt in node_types:
                graphql_types[nt] = static_type
            self._cached_graphql_types = graphql_types
            return graphql_types

        class_name_manager = VariableNameManager()
        graphql_types: dict[str, type[GraphQLBuilder.GraphNode]] = {}
        for node_type in node_types:
            class_name = class_name_manager.make_valid(node_type.capitalize())
            type_name = f"{class_name}{'' if node_type.lower().endswith('node') else 'Node'}"
            fields = [
                strawberry.field(name='neighbors', resolver=self._make_neighbors_resolver(node_type)),
                strawberry.field(name='edges', resolver=self._make_edges_resolver()),
            ]

            if (
                    self._node_value_graphql_type_supplier is not None
                    and (value_graphql_type := self._node_value_graphql_type_supplier(node_type)) is not None
            ):
                value_field = strawberry.field(name='value', default=None)
                value_field.type = list[value_graphql_type] | None
                fields.append(value_field)

            graphql_types[node_type] = self._create_node_type(
                name=type_name,
                fields=fields,
                description=f"Represents a {node_type.capitalize()} Graph Node",
            )

        self._cached_graphql_types = graphql_types
        return graphql_types

    def _graphql_query(self):
        inflection = inflect.engine()
        builder = self
        _ = self._graphql_types

        def graphql_graph(info: Info) -> GraphQLBuilder.Graph:
            return GraphQLBuilder.Graph(nx_graph=builder._resolve_graph(info))

        def graph_nodes_resolver(
                graphql_type: type[GraphQLBuilder.GraphNode] | None = None,
                node_type: str | None = None,
                resolver_name: str = 'nodes',
        ):
            return_annotation = list[graphql_type] if graphql_type is not None else list[GraphQLBuilder.GraphNode]

            def graph_nodes(
                    info: Info,
                    node_id: strawberry.ID | None = strawberry.UNSET,
            ) -> return_annotation:
                decoded_node_id = node_id and decode_node_id(node_id)
                graph = builder._resolve_graph(info)

                if graphql_type:
                    nodes = (
                        GraphQLBuilder._graph_node(graphql_type, n, d)
                        for n, d in graph.nodes(data=True)
                    )
                else:
                    nodes = (
                        GraphQLBuilder._graph_node(builder._resolve_node_class(d['type']), n, d)
                        for n, d in graph.nodes(data=True)
                    )

                def filter_node(node):
                    output = True
                    if node_type:
                        output = node.type.lower() == node_type
                    if decoded_node_id:
                        output = output and (decode_node_id(node.id) == decoded_node_id)
                    return output

                return [node for node in nodes if filter_node(node)]

            graph_nodes.__name__ = resolver_name
            return graph_nodes

        def graph_edges(
                info: Info,
                edge_id: strawberry.ID | None = strawberry.UNSET,
        ) -> list[GraphQLBuilder.GraphEdge]:
            decoded_edge_id = edge_id and decode_edge_id(edge_id)
            graph = builder._resolve_graph(info)
            edges = (
                builder._graph_edge((source, target), data, graph=graph)
                for source, target, data in graph.edges(data=True)
            )
            if decoded_edge_id:
                return [edge for edge in edges if decode_edge_id(edge.id) == decoded_edge_id]
            return list(edges)

        def graph_measure(
                info: Info,
                measure: GraphQLBuilder.GraphMeasure,
        ) -> GraphQLBuilder.Measure:
            graph = builder._resolve_graph(info)
            if isinstance(measure.value, str):
                method = measure.value
                module = nx
            else:
                method = measure.value[1]
                module = importlib.import_module(measure.value[0])

            value_getter = operator.attrgetter(method)(module)
            value = float(value_getter(graph))
            return GraphQLBuilder.Measure(name=measure.name, value=value)

        query_fields = [
            strawberry.field(name='graph', resolver=graphql_graph),
            strawberry.field(name='nodes', resolver=graph_nodes_resolver(resolver_name='nodes')),
            strawberry.field(name='edges', resolver=graph_edges),
            strawberry.field(name='measure', resolver=graph_measure),
        ]

        if self.mode == SchemaMode.DYNAMIC:
            field_name_manager = VariableNameManager()
            for node_type, graphql_type in self._graphql_types.items():
                field_name = field_name_manager.make_valid(inflection.plural(node_type))
                resolver = graph_nodes_resolver(graphql_type, node_type, resolver_name=field_name)
                field_params: dict[str, Any] = {'resolver': resolver}
                if self.dynamic_field_naming == DynamicFieldNaming.EXPLICIT:
                    field_params['name'] = field_name

                query_fields.append(strawberry.field(**field_params))

        return create_type(name='Query', fields=query_fields)

    def _graphql_mutation(self):
        refresh_graph = functools.partial(super().build, **self._cached_build_kwargs)

        @strawberry.type
        class Mutation:

            @strawberry.mutation
            def refresh(self) -> bool:
                refresh_graph()
                return True

        return Mutation

    def schema(self, config: StrawberryConfig | None = None) -> strawberry.Schema:
        unique_types = list({id(t): t for t in self._graphql_types.values()}.values())
        inf_number_scalar = strawberry.scalar(
            name='InfNumber',
            description='Integer, Decimal or Float including Infinity and -Infinity',
            serialize=converters.infnum_to_value,
            parse_value=converters.value_to_infnum,
        )
        if config is None:
            schema_config = StrawberryConfig(
                scalar_map={GraphQLBuilder.InfNumber: inf_number_scalar}
            )
        else:
            schema_config = config
            if schema_config.scalar_map is None:
                schema_config.scalar_map = {}
            if GraphQLBuilder.InfNumber not in schema_config.scalar_map:
                schema_config.scalar_map[GraphQLBuilder.InfNumber] = inf_number_scalar

        return strawberry.Schema(
            query=self._graphql_query(),
            mutation=self._graphql_mutation(),
            types=unique_types,
            extensions=[
                lambda: ParserCache(maxsize=100),
                lambda: QueryDepthLimiter(max_depth=10),
                lambda: ValidationCache(maxsize=100),
            ],
            config=schema_config,
        )

    def build(
            self,
            node_value_graphql_type_supplier: Callable[[str], StrawberryType | None] | None = None,
            config: StrawberryConfig | None = None,
            **kwargs: Any,
    ) -> strawberry.Schema | None:
        """Build a Strawberry GraphQL Schema.

        Args:
            node_value_graphql_type_supplier: Callable[[str], StrawberryType]
            config: Optional StrawberryConfig instance
            **kwargs: Additional build arguments

        Returns:
            Strawberry GraphQL Schema
        """
        self._cached_graphql_types = None
        super().build(**kwargs)

        self._node_value_graphql_type_supplier = node_value_graphql_type_supplier

        return self.schema(config=config)

    async def abuild(
            self,
            node_value_graphql_type_supplier: Callable[[str], StrawberryType | None] | None = None,
            config: StrawberryConfig | None = None,
            **kwargs: Any,
    ) -> strawberry.Schema | None:
        """Asynchronously build a Strawberry GraphQL Schema.

        Args:
            node_value_graphql_type_supplier: Callable[[str], StrawberryType]
            config: Optional StrawberryConfig instance
            **kwargs: Additional build arguments

        Returns:
            Strawberry GraphQL Schema
        """
        self._cached_graphql_types = None
        await super().abuild(**kwargs)

        self._node_value_graphql_type_supplier = node_value_graphql_type_supplier

        return self.schema(config=config)
