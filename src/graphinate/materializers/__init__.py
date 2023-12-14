import functools
import json
import os
from collections.abc import Mapping
from enum import Enum
from typing import Callable, Optional

from .. import builders, modeling, server
from ..tools.gui import modal_radiobutton_chooser
from .matplotlib import plot

ENABLE_GUI = bool(os.getenv('GRAPHINATE_ENABLE_GUI', True))


class Materializers(Enum):
    """Materializers Enum

    Attributes:
        D3Graph: create a D3 Graph and print it to stdout
        GraphQL: create a GraphQL Schema and serve it in a web server
        NetworkX: create a NetworkX Graph and plot+show it with matplotlib
        NetworkX_with_edge_labels: create a NetworkX Graph and plot+show it with matplotlib
    """
    D3Graph: tuple = (builders.D3Builder, lambda d: print(json.dumps(d, indent=2, default=str)))
    GraphQL: tuple = (builders.GraphQLBuilder, server.graphql)
    NetworkX: tuple = (builders.NetworkxBuilder, plot)
    NetworkX_with_edge_labels: tuple = (builders.NetworkxBuilder, functools.partial(plot, with_edge_labels=True))


def materialize(model: modeling.GraphModel,
                title: Optional[str] = None,
                graph_type: builders.GraphType = builders.GraphType.Graph,
                default_node_attributes: Optional[Mapping] = None,
                builder: Optional[type[builders.Builder]] = None,
                actualizer: Optional[Callable] = None,
                **kwargs):
    """

    Args:
        model: GraphModel
        title: the GraphModel name
        graph_type: GraphType
        default_node_attributes:
        builder: Builder instance
        actualizer: function that will consume the resulting built graph and
                    actualises it (e.g., display, serves, print etc.)
        **kwargs:

    Returns:
        None
    """
    title = title or model.name
    if ENABLE_GUI and builder is None and actualizer is None:
        result = modal_radiobutton_chooser(title,
                                           options={m.name: m.value for m in Materializers},
                                           default=(None, None))
        builder, actualizer = result[1]

    if builder is None and actualizer is None:
        raise ValueError("Missing: builder, actualizer")

    if builder:
        graph = builders.build(builder,
                               model,
                               graph_type,
                               default_node_attributes=default_node_attributes,
                               **kwargs)

        if actualizer and callable(actualizer):
            actualizer(graph)
        else:
            print(graph)


__all__ = ('materialize', 'plot')
