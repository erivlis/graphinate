from typing import List

import strawberry
from strawberry import ID

from .d3 import D3Graph
from ..modeling import GraphModel


@strawberry.interface
class Element:
    label: str
    color: str
    type: str
    value: strawberry.scalars.JSON


@strawberry.type
class Node(Element):
    id: object
    lineage: List[object]


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


class GraphqlGraph(D3Graph):

    def __init__(self, model: GraphModel):
        super().__init__(model)

    def build(self, **kwargs) -> Graph:
        d3_graph: dict = super().build(**kwargs)

        data = {k: v for k, v in d3_graph.items() if k not in ('nodes', 'links')}
        nodes = [Node(id=node['id'],
                      lineage=node['lineage'],
                      label=node['label'],
                      color=node['color'],
                      type=node['type'],
                      value=node['value'])
                 for node in d3_graph['nodes']]

        edges = [Edge(source=edge['source'],
                      target=edge['target'],
                      weight=edge['weight'],
                      label=edge.get('label'),
                      color=edge.get('color'),
                      type=edge.get('type'),
                      value=edge.get('value'))
                 for edge in d3_graph['links']]

        return Graph(data=data, nodes=nodes, edges=edges)
