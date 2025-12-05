import json
from typing import Any, Literal

import mappingtools
import networkx as nx

from .. import color
from ..enums import GraphType
from ..modeling import GraphModel
from ._networkx import NetworkxBuilder


class D3Builder(NetworkxBuilder):
    """Build a D3 Graph"""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    def build(self, values_format: Literal['json', 'python'] = 'python', **kwargs: Any) -> dict:
        """
        Args:
            values_format: Literal['python', 'json'] - The format of the values
            **kwargs:

        Returns:
            D3 Graph
        """
        super().build(**kwargs)
        color.convert_colors_to_hex(self._graph)
        d3graph: dict = self.from_networkx(self._graph)

        match values_format:
            case 'json':
                return mappingtools.transformers.strictify(d3graph, value_converter=json.dumps)
            case 'python':
                return d3graph
            case _:
                raise ValueError(f"Invalid values format: {values_format}")

    @staticmethod
    def from_networkx(nx_graph: nx.Graph) -> dict:
        d3_graph: dict = nx.node_link_data(nx_graph, nodes='nodes', edges='links')
        return d3_graph
