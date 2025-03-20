import functools
import json
from collections.abc import Callable, Mapping
from enum import Enum
from typing import Optional

from graphinate import GraphModel, GraphType, builders, graphql, matplotlib


class Materializers(Enum):
    """Materializers Enum

    Attributes:
        D3Graph: create a D3 Graph and print it to stdout
        GraphQL: create a GraphQL Schema and serve it in a web server
        NetworkX: create a NetworkX Graph and plot+show it with matplotlib
        NetworkX_with_edge_labels: create a NetworkX Graph and plot+show it with matplotlib
    """
    D3Graph: tuple = (builders.D3Builder, lambda d: print(json.dumps(d, indent=2, default=str)))
    GraphQL: tuple = (builders.GraphQLBuilder, graphql.server)
    NetworkX: tuple = (builders.NetworkxBuilder, matplotlib.plot)
    NetworkX_with_edge_labels: tuple = (builders.NetworkxBuilder,
                                        functools.partial(matplotlib.plot, with_edge_labels=True))
    Mermaid: tuple = (builders.MermaidBuilder, print)


def materialize(model: GraphModel,
                graph_type: GraphType = GraphType.Graph,
                default_node_attributes: Optional[Mapping] = None,
                builder: Optional[type[builders.Builder]] = None,
                builder_output_handler: Optional[Callable] = None,
                **kwargs):
    """
    Materialize a GraphModel using a Builder and an Actualizer

    Args:
        model: GraphModel - the model to be materialized
        graph_type: GraphType - the type of graph to be built.
                                Default is Graph.
        default_node_attributes: Mapping - A Mapping containing attributes that are added to all nodes.
        builder: Builder - the builder to be used to build the graph.
        builder_output_handler: function that will consume the resulting built graph and
                    outputs it (e.g., display, serve, print, etc.).
        **kwargs:


    Returns:
        None
    """
    if builder is None and builder_output_handler is None:
        raise ValueError("Missing: builder, builder_output_handler")

    if builder:
        graph = builders.build(builder,
                               model,
                               graph_type,
                               default_node_attributes=default_node_attributes,
                               **kwargs)

        if builder_output_handler and callable(builder_output_handler):
            builder_output_handler(graph, **kwargs)
        else:
            print(graph)
