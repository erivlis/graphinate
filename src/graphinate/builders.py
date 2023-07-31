import base64
import functools
import importlib
import json
import operator
from collections import Counter
from enum import Enum
from types import MappingProxyType
from typing import Union, Hashable, Optional, List, Callable, Type, Dict, Iterable, Mapping

import inflect
import networkx as nx
import strawberry
from loguru import logger
from strawberry import ID

from . import mutate
from .modeling import GraphModel, UNIVERSE_NODE
from .typing import NodeTypeAbsoluteId


class GraphType(Enum):
    Graph = nx.Graph
    DiGraph = nx.DiGraph
    MultiDiGraph = nx.MultiDiGraph
    MultiGraph = nx.MultiGraph


class NetworkxBuilder:
    default_node_attributes: Mapping = MappingProxyType({
        'type': 'node',
        'label': str,
        'value': None,
        'color': 'blue',
        'lineage': None
    })

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        self.model = model
        self.graph_type = graph_type

    def _initialize_graph(self):
        self._graph = self.graph_type.value(name=self.model.name, types=Counter())

    def _populate_node_type(self, node_type: Union[Hashable, UNIVERSE_NODE] = UNIVERSE_NODE, **kwargs):
        for parent_node_type, child_node_types in self.model.node_children(node_type).items():
            for child_node_type in child_node_types:
                node_type_absolute_id = (parent_node_type, child_node_type)
                self._populate_nodes(node_type_absolute_id, **kwargs)

    @staticmethod
    def _parent_node_id(node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
        if node_type_absolute_id[0] is UNIVERSE_NODE:
            return UNIVERSE_NODE
        else:
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
            self._graph.add_node(node_id,
                                 label=label,
                                 color='type',
                                 type=node_type,
                                 value=node.value,
                                 lineage=list(node_lineage))

            self._graph.graph['types'].update({node_type: 1})

            if node_model.parent_type is not UNIVERSE_NODE:
                logger.debug("Adding edge from: '{}' to '{}'", parent_node_id, node_id)
                self._graph.add_edge(parent_node_id, node_id)

            new_kwargs = kwargs.copy()
            new_kwargs[f"{node_type}_id"] = node.key
            self._populate_node_type(node_model.type, **new_kwargs)

    def _populate_edges(self, **kwargs):
        for edge_type, edge_generators in self.model.edge_generators.items():
            for edge_generator in edge_generators:
                for edge in edge_generator(**kwargs):
                    edge_attributes = {
                        'type': edge_type,
                        'label': edge.label,
                        'value': edge.value,
                        'weight': edge.weight
                    }
                    logger.debug("Adding edge from: '{}' to: '{}'", edge.source, edge.target)
                    self._graph.add_edge((edge.source,), (edge.target,), **edge_attributes)

    def _rectify_node_attributes(self, **defaults):
        for _type, default in defaults.items():
            if callable(default):
                attributes = {n: default(n) for n, a in self._graph.nodes(data=_type, default=None) if a is None}
            elif default:
                attributes = {n: a for n, a in self._graph.nodes(data=_type, default=default) if a == default}
            else:
                attributes = {n: n for n, a in self._graph.nodes(data=_type, default=default) if a is default}

            nx.set_node_attributes(self._graph, attributes, _type)

    def _finalize_graph(self, **defaults):
        types_counter = self._graph.graph['types']
        self._rectify_node_attributes(**defaults)
        self._graph.graph['types'] = mutate.dictify(types_counter)

    def build(self, default_node_attributes: Mapping = default_node_attributes, **kwargs):
        self.model.rectify()
        self._initialize_graph()
        self._populate_node_type(**kwargs)
        self._populate_edges(**kwargs)
        self._finalize_graph(**self.default_node_attributes)
        return self._graph


class D3Builder(NetworkxBuilder):

    def __init__(self, model: GraphModel):
        super().__init__(model)

    def build(self, **kwargs) -> dict:
        nx_graph: nx.Graph = super().build(**kwargs)
        return self.from_networkx(nx_graph)

    @staticmethod
    def from_networkx(nx_graph: nx.Graph):
        d3_graph = nx.node_link_data(nx_graph)
        return mutate.dictify_tuple(d3_graph)


# region Simple GraphQL Builder


class GenericGraphQLBuilder(D3Builder):

    def __init__(self, model: GraphModel):
        super().__init__(model)

    def _schema(self, d3_graph) -> strawberry.Schema:
        data = {k: v for k, v in d3_graph.items() if k not in ('nodes', 'links')}

        @strawberry.interface
        class Element:
            label: str
            color: Optional[str] = None
            type: str
            value: strawberry.scalars.JSON

        @strawberry.type
        class Node(Element):
            id: ID
            lineage: List[str]

        @strawberry.type
        class Edge(Element):
            source: ID
            target: ID
            weight: float

        @strawberry.type
        class Graph:
            data: strawberry.scalars.JSON
            nodes: List[Node]
            edges: List[Edge]

        nodes = [Node(id=str(node['id']),
                      lineage=node.get('lineage', []),
                      label=node.get('label', str(node['id'])),
                      color=node.get('color'),
                      type=node.get('type', 'Node'),
                      value=json.dumps(node.get('value', node['id'])))
                 for node in d3_graph['nodes']]

        edges = [Edge(source=str(edge['source']),
                      target=str(edge['target']),
                      weight=edge.get('weight', 1.0),
                      label=edge.get('label', ''),
                      color=edge.get('color', ''),
                      type=edge.get('type', ''),
                      value=json.dumps(edge.get('value')))
                 for edge in d3_graph['links']]

        def get_graph():
            return Graph(data=data, nodes=nodes, edges=edges)

        @strawberry.type
        class Query:
            graph: Graph = strawberry.field(resolver=get_graph)

        return strawberry.Schema(query=Query)

    def build(self, **kwargs) -> strawberry.Schema:
        d3_graph: dict = super().build(**kwargs)
        return self._schema(d3_graph)


# endregion Simple GraphQL Builder


class TypedGraphQLBuilder(NetworkxBuilder):
    _id_delimiter = '»'

    @strawberry.type
    class Graph:
        name: str
        types: strawberry.scalars.JSON
        node_count: int
        edge_count: int
        size: int
        order: int
        average_degree: float
        weisfeiler_lehman_graph_hash: str

    @strawberry.interface
    class GraphNode:
        id: ID
        label: str
        color: str
        type: str
        value: Optional[strawberry.scalars.JSON]
        lineage: str
        neighbors: Optional[List['TypedGraphQLBuilder.GraphNode']]
        children: Optional[List['TypedGraphQLBuilder.GraphNode']]

    @strawberry.enum
    class Measure(Enum):
        """
        See Netweorkx documentation for explanations:
        https://networkx.org/documentation/stable/reference/index.html
        """

        is_empty = 'is_empty'
        is_directed = 'is_directed'
        is_weighted = 'is_weighted'
        is_negatively_weighted = 'is_negatively_weighted'
        """
        A graph is planar iff it can be drawn in a plane without any edge intersections.
        """
        is_planar = 'is_planar'
        """
        A regular graph is a graph where each vertex has the same degree. A regular digraph is a graph where the
        indegree and outdegree of each vertex are equal.
        """
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

        """
        A graph is biconnected if, and only if, it cannot be disconnected by removing only one node (and all edges
        incident on that node). If removing a node increases the number of disconnected components in the graph, that
        node is called an articulation point, or cut vertex. A biconnected graph has no articulation points.
        """
        is_biconnected = 'is_biconnected'
        """
        A directed graph is strongly connected if and only if every vertex in the graph is reachable from every other
        vertex.
        """
        is_strongly_connected = 'is_strongly_connected'

        """
        A directed graph is weakly connected if and only if the graph is connected when the direction of the edge
        between nodes is ignored.
        """
        is_weakly_connected = 'is_weakly_connected'

        """
        A graph is semiconnected if, and only if, for any pair of nodes, either one is reachable from the other,
        or they are mutually reachable.
        """
        is_semiconnected = 'is_semiconnected'
        is_attracting_component = 'is_attracting_component'
        is_tournament = ('networkx.algorithms.tournament', 'is_tournament')
        is_tree = 'is_tree'
        is_forest = 'is_forest'
        is_arborescence = 'is_arborescence'
        is_branching = 'is_branching'
        is_triad = 'is_triad'
        diameter = 'diameter'
        radius = 'radius'
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

    def __init__(self, model: GraphModel):
        super().__init__(model)

    @staticmethod
    def _encode_id(graph_node_id: tuple, encoding: str = 'utf-8'):
        msg = TypedGraphQLBuilder._id_delimiter.join(graph_node_id)
        msg_bytes = msg.encode(encoding)
        b64_bytes = base64.b85encode(msg_bytes)
        b64_msg = b64_bytes.decode(encoding)
        return b64_msg

    @staticmethod
    def _decode_id(graphql_node_id: strawberry.ID, encoding: str = 'utf-8'):
        b64_bytes = graphql_node_id.encode(encoding)
        msg_bytes = base64.b85decode(b64_bytes)
        msg = msg_bytes.decode(encoding)
        output = tuple(msg.split(TypedGraphQLBuilder._id_delimiter))
        return output

    @staticmethod
    def _graph_node(node_class: Type['TypedGraphQLBuilder.GraphNode'], node: tuple,
                    node_data: dict) -> 'TypedGraphQLBuilder.GraphNode':
        kwargs = {
            'id': TypedGraphQLBuilder._encode_id(node),
            'label': node_data['label'],
            'color': node_data['color'],
            'type': node_data['type'],
            'value': json.dumps(node_data['value']),
            'lineage': str(node_data['lineage']),
        }

        return node_class(**kwargs)

    @functools.lru_cache()
    def _children_types(self, node_type: str):
        return self.model.node_children(node_type).get(node_type, [])

    @functools.lru_cache()
    def _graphql_types(self, graph: nx.Graph) -> Dict[str, Type['TypedGraphQLBuilder.GraphNode']]:

        graphql_types: Dict[str, Type['TypedGraphQLBuilder.GraphNode']] = {}

        # Create classes for nodes accordong to thier type
        for node_model in self.model.node_models.values():
            class_name = node_model.type.capitalize()
            bases = (TypedGraphQLBuilder.GraphNode,)
            class_dict = {
                '__doc__': f"A {node_model.type.capitalize()} Graph Node",
            }
            # noinspection PyTypeChecker
            graphql_type: Type['TypedGraphQLBuilder.GraphNode'] = type(class_name, bases, class_dict)
            graphql_types[node_model.type] = graphql_type

        def neighbors_resolver(neighbors_types: Optional[Iterable[str]] = None) -> Callable[
            ['TypedGraphQLBuilder.GraphNode'], List['TypedGraphQLBuilder.GraphNode']]:
            def neighbors(self, children: bool = False) -> Optional[List['TypedGraphQLBuilder.GraphNode']]:
                node = TypedGraphQLBuilder._decode_id(self.id)
                items = (TypedGraphQLBuilder._graph_node(graphql_types[d['type']], n, d)
                         for n, d in graph.nodes(data=True) if n in graph.neighbors(node))

                if children and neighbors_types:
                    return [item for item in items if item.type in neighbors_types]

                return list(items)

            return neighbors

        node_types = self.model.node_types
        for node_type in node_types:
            children_types = set(self._children_types(node_type))
            graphql_types[node_type].neighbors = strawberry.field(resolver=neighbors_resolver())
            graphql_types[node_type].children = strawberry.field(resolver=neighbors_resolver(children_types))

        return {k: strawberry.type(v, name=k.capitalize() if k.lower().endswith('node') else f"{k.capitalize()}Node")
                for k, v in graphql_types.items()}

    def _graphql_query(self, graph: nx.Graph):
        def graph_nodes_resolver(graphql_type: Type['TypedGraphQLBuilder.GraphNode'],
                                 node_type: str) -> Callable[[], list['TypedGraphQLBuilder.GraphNode']]:
            def graph_nodes() -> Optional[List['TypedGraphQLBuilder.GraphNode']]:
                return [TypedGraphQLBuilder._graph_node(graphql_type, n, d)
                        for n, d in graph.nodes(data=True)
                        if d['type'].lower() == node_type]

            return graph_nodes

        graphql_types = self._graphql_types(graph)

        inflection = inflect.engine()

        query_class_dict = {'__annotations__': {}}

        # definitions for GraphQL types implementing 'GraphNode' GraphQL interface
        for node_type, graphql_type in graphql_types.items():
            field_name = inflection.plural(node_type)
            query_class_dict[field_name] = strawberry.field(resolver=graph_nodes_resolver(graphql_type, node_type))
            query_class_dict['__annotations__'][field_name] = 'Optional[List[TypedGraphQLBuilder.GraphNode]]'

        # definition for 'Graph' GraphQL object type
        query_class_dict['graph'] = strawberry.field(
            resolver=lambda: TypedGraphQLBuilder.Graph(
                name=graph.graph['name'],
                types=json.dumps(graph.graph['types']),
                node_count=graph.number_of_nodes(),
                edge_count=graph.number_of_edges(),
                order=graph.order(),
                size=graph.size(weight='weight'),
                average_degree=1.0 * sum(d for _, d in graph.degree()) / graph.order(),
                weisfeiler_lehman_graph_hash=nx.weisfeiler_lehman_graph_hash(graph)
            )
        )
        query_class_dict['__annotations__']['graph'] = 'TypedGraphQLBuilder.Graph'

        # definition for 'GraphMeasure' GraphQL type
        @strawberry.field()
        async def graph_measure(measure: TypedGraphQLBuilder.Measure) -> float:
            if isinstance(measure.value, str):
                method = measure.value
                module = nx
            else:
                method = measure.value[1]
                module = importlib.import_module(measure.value[0])

            measure = operator.attrgetter(method)(module)
            return float(measure(graph))

        query_class_dict['graph_measure'] = graph_measure
        query_class_dict['__annotations__']['graph_measure'] = 'float'

        # definition of GraphQL root Query object type
        query_graphql_type = strawberry.type(type('Query', tuple(), query_class_dict), name='Query')

        return query_graphql_type

    def _schema(self, graph: nx.Graph) -> strawberry.Schema:

        query_graphql_type = self._graphql_query(graph)
        graphql_types = self._graphql_types(graph)

        # define and return Schema
        return strawberry.Schema(
            query=query_graphql_type,
            types=graphql_types.values()
        )

    def build(self, **kwargs):
        nx_graph: nx.Graph = super().build(**kwargs)
        schema: strawberry.Schema = self._schema(nx_graph)
        return schema
