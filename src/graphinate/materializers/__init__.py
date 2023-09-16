import functools
import json
import os
from collections.abc import Mapping
from enum import Enum
from pprint import pprint
from typing import Callable, Optional

from .. import builders, modeling, server
from ..tools.gui import modal_radiobutton_chooser
from .matplotlib import plot

ENABLE_GUI = bool(os.getenv('GRAPHINATE_ENABLE_GUI', True))

graphql = server.run_graphql


class Materializers(Enum):
    NetworkX = (builders.NetworkxBuilder, plot)
    NetworkX_with_edge_labels = (builders.NetworkxBuilder, functools.partial(plot, with_edge_labels=True))
    D3Graph = (builders.D3Builder, lambda d: print(json.dumps(d, indent=2, default=str)))
    GraphQL = (builders.GraphQLBuilder, graphql)


def materialize(model: modeling.GraphModel,
                title: Optional[str] = None,
                graph_type: builders.GraphType = builders.GraphType.Graph,
                default_node_attributes: Optional[Mapping] = None,
                builder: Optional[type[builders.Builder]] = None,
                actualizer: Optional[Callable] = None,
                **kwargs):
    title = title or model.name
    if ENABLE_GUI and builder is None and actualizer is None:
        result = modal_radiobutton_chooser(title,
                                           options={m.name: m.value for m in Materializers},
                                           default=(None, None))
        if result[0]:
            builder, actualizer = result[1]

    materialized_graph = builders.build(builder,
                                        model,
                                        graph_type,
                                        default_node_attributes=default_node_attributes,
                                        **kwargs)

    actualizer(materialized_graph)


__all__ = ('materialize', 'plot', 'graphql')
