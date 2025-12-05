from enum import Enum

import networkx as nx
from typing_extensions import Self


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
    def of(cls, graph: nx.Graph) -> Self:
        """Determine the graph type based on structure and properties.

        Args:
            graph (nx.Graph): A NetworkX graph object.

        Returns:
            GraphType: An instance of this Enum matching the input graph.
        """
        if graph.is_directed() and graph.is_multigraph():
            return cls.MultiDiGraph
        elif graph.is_directed():
            return cls.DiGraph
        elif graph.is_multigraph():
            return cls.MultiGraph
        else:
            return cls.Graph
