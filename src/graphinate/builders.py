import base64
import functools
import json
from collections import Counter
from enum import Enum
from typing import Union, Hashable, Optional, List, Callable, Type, Dict, Iterable

import inflect
import networkx as nx
import strawberry
from loguru import logger
from strawberry import ID

from graphinate import GraphModel, mutate
from graphinate.modeling import UNIVERSE_NODE
from graphinate.typing import NodeTypeAbsoluteId


class GraphType(Enum):
    Graph = nx.Graph
    DiGraph = nx.DiGraph
    MultiDiGraph = nx.MultiDiGraph
    MultiGraph = nx.MultiGraph


class NetworkxBuilder:

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        self.model = model
        self.graph_type = graph_type

    def _init_graph(self):
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

    def _finalize(self):
        types_counter = self._graph.graph['types']
        self._graph.graph['types'] = dict(types_counter)

    def build(self, **kwargs):
        self._init_graph()
        self._populate_node_type(**kwargs)
        self._populate_edges(**kwargs)
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


@strawberry.interface
class Element:
    label: str
    color: Optional[str] = None
    type: str
    value: str


@strawberry.type
class Node(Element):
    id: str
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


class SimpleGraphQLBuilder(D3Builder):

    def __init__(self, model: GraphModel):
        super().__init__(model)

    def build(self, **kwargs) -> strawberry.Schema:
        d3_graph: dict = super().build(**kwargs)

        data = {k: v for k, v in d3_graph.items() if k not in ('nodes', 'links')}
        nodes = [GraphNode(id=str(node['id']),
                           lineage=node['lineage'],
                           label=node['label'],
                           color=node['color'],
                           type=node['type'],
                           value=str(node['value']))
                 for node in d3_graph['nodes']]

        edges = [Edge(source=str(edge['source']),
                      target=str(edge['target']),
                      weight=edge['weight'],
                      label=edge.get('label'),
                      color=edge.get('color'),
                      type=edge.get('type'),
                      value=str(edge.get('value')))
                 for edge in d3_graph['links']]

        def get_graph():
            return Graph(data=data, nodes=nodes, edges=edges)

        @strawberry.type
        class Query:
            graph: Graph = strawberry.field(resolver=get_graph)

        return strawberry.Schema(query=Query)


# endregion Simple GraphQL Builder


@strawberry.interface
class GraphNode:
    id: ID
    label: str
    color: str
    type: str
    value: Optional[strawberry.scalars.JSON]
    lineage: str
    children: Optional[List['GraphNode']]


class GraphQLBuilder(NetworkxBuilder):
    _id_delimiter = '»'

    def __init__(self, model: GraphModel):
        super().__init__(model)

    @staticmethod
    def _encode_id(graph_node_id: tuple, encoding: str = 'utf-8'):
        msg = GraphQLBuilder._id_delimiter.join(graph_node_id)
        msg_bytes = msg.encode(encoding)
        b64_bytes = base64.b85encode(msg_bytes)
        b64_msg = b64_bytes.decode(encoding)
        return b64_msg

    @staticmethod
    def _decode_id(graphql_node_id: strawberry.ID, encoding: str = 'utf-8'):
        b64_bytes = graphql_node_id.encode(encoding)
        msg_bytes = base64.b85decode(b64_bytes)
        msg = msg_bytes.decode(encoding)
        output = tuple(msg.split(GraphQLBuilder._id_delimiter))
        return output

    @staticmethod
    def _graph_node(node_class: Type[GraphNode], node: tuple, node_data: dict) -> GraphNode:
        kwargs = {
            'id': GraphQLBuilder._encode_id(node),
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

    def _graphql_types(self, graph: nx.Graph) -> Dict[str, Type[GraphNode]]:

        graphql_types: Dict[str, Type[GraphNode]] = {}
        for node_model in self.model.node_models.values():
            # bases = (GraphNode,) if self._children_types(node_model.type) else (GraphNode,)
            class_name = node_model.type.capitalize()
            bases = (GraphNode,)
            class_dict = {
                '__doc__': f"A {node_model.type.capitalize()} Graph Node",
            }
            # noinspection PyTypeChecker
            graphql_type: Type[GraphNode] = type(class_name, bases, class_dict)
            graphql_types[node_model.type] = graphql_type

        def resolver(children_types: Iterable[str]) -> Callable[[GraphNode], List[GraphNode]]:
            def get_children(self) -> Optional[List[GraphNode]]:
                node = GraphQLBuilder._decode_id(self.id)
                if children_types:
                    return [GraphQLBuilder._graph_node(graphql_types[d['type']], n, d)
                            for n, d in graph.nodes(data=True)
                            if n in graph.neighbors(node) and d['type'] in children_types]

            return get_children

        node_types = self.model.node_types
        for node_type in node_types:
            children_types = set(self._children_types(node_type))
            graphql_types[node_type].children = strawberry.field(resolver=resolver(children_types))

        return {k: strawberry.type(v, name=f"{k.capitalize()}Node")
                for k, v in graphql_types.items()}

    def _schema(self, graph: nx.Graph) -> strawberry.Schema:
        def resolver(graphql_type: Type[GraphNode], node_type: str) -> Callable[[], list[GraphNode]]:
            def get_nodes() -> Optional[List[GraphNode]]:
                return [GraphQLBuilder._graph_node(graphql_type, n, d)
                        for n, d in graph.nodes(data=True)
                        if d['type'].lower() == node_type]

            return get_nodes

        graphql_types = self._graphql_types(graph)

        inflection = inflect.engine()
        query_class_dict = {'__annotations__': {}}
        for node_type, graphql_type in graphql_types.items():
            field_name = inflection.plural(node_type)
            query_class_dict[field_name] = strawberry.field(resolver=resolver(graphql_type, node_type))
            query_class_dict['__annotations__'][field_name] = 'Optional[List[GraphNode]]'

        query_type = strawberry.type(type('Query', tuple(), query_class_dict), name='Query')

        return strawberry.Schema(
            query=query_type,
            types=graphql_types.values()
        )

    def build(self, **kwargs):
        nx_graph: nx.Graph = super().build(**kwargs)

        schema = self._schema(nx_graph)

        return schema