import networkx as nx

from .networkx import NetworkxGraph
from .. import mutate
from ..modeling import GraphModel


class D3Graph(NetworkxGraph):

    def __init__(self, model: GraphModel):
        super().__init__(model)

    def build(self, **kwargs) -> dict:
        nx_graph: nx.Graph = super().build(**kwargs)
        graph = nx.node_link_data(nx_graph)
        return mutate.dictify(graph)
