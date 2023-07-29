import base64
import functools
import json
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


# @strawberry.interface
# class GraphNode:
#     id: ID
#     label: str
#     color: str
#     type: str
#     value: Optional[strawberry.scalars.JSON]
#     lineage: str
#     children: Optional[List['GraphNode']]


class TypedGraphQLBuilder(NetworkxBuilder):
    _id_delimiter = '»'

    @strawberry.interface
    class GraphNode:
        id: ID
        label: str
        color: str
        type: str
        value: Optional[strawberry.scalars.JSON]
        lineage: str
        children: Optional[List['TypedGraphQLBuilder.GraphNode']]

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

    def _graphql_types(self, graph: nx.Graph) -> Dict[str, Type['TypedGraphQLBuilder.GraphNode']]:

        graphql_types: Dict[str, Type['TypedGraphQLBuilder.GraphNode']] = {}
        for node_model in self.model.node_models.values():
            class_name = node_model.type.capitalize()
            bases = (TypedGraphQLBuilder.GraphNode,)
            class_dict = {
                '__doc__': f"A {node_model.type.capitalize()} Graph Node",
            }
            # noinspection PyTypeChecker
            graphql_type: Type['TypedGraphQLBuilder.GraphNode'] = type(class_name, bases, class_dict)
            graphql_types[node_model.type] = graphql_type

        def children_resolver(children_types: Iterable[str]) -> Callable[
            ['TypedGraphQLBuilder.GraphNode'], List['TypedGraphQLBuilder.GraphNode']]:
            def children(self) -> Optional[List['TypedGraphQLBuilder.GraphNode']]:
                node = TypedGraphQLBuilder._decode_id(self.id)
                if children_types:
                    return [TypedGraphQLBuilder._graph_node(graphql_types[d['type']], n, d)
                            for n, d in graph.nodes(data=True)
                            if n in graph.neighbors(node) and d['type'] in children_types]

            return children

        node_types = self.model.node_types
        for node_type in node_types:
            children_types = set(self._children_types(node_type))
            graphql_types[node_type].children = strawberry.field(resolver=children_resolver(children_types))

        return {k: strawberry.type(v, name=k.capitalize() if k.lower().endswith('node') else f"{k.capitalize()}Node")
                for k, v in graphql_types.items()}

    def _schema(self, graph: nx.Graph) -> strawberry.Schema:
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
        for node_type, graphql_type in graphql_types.items():
            field_name = inflection.plural(node_type)
            query_class_dict[field_name] = strawberry.field(resolver=graph_nodes_resolver(graphql_type, node_type))
            query_class_dict['__annotations__'][field_name] = 'Optional[List[TypedGraphQLBuilder.GraphNode]]'

        query_type = strawberry.type(type('Query', tuple(), query_class_dict), name='Query')

        return strawberry.Schema(
            query=query_type,
            types=graphql_types.values()
        )

    def build(self, **kwargs):
        nx_graph: nx.Graph = super().build(**kwargs)
        schema: strawberry.Schema = self._schema(nx_graph)
        return schema
