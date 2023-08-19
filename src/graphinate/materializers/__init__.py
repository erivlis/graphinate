from collections.abc import Mapping
from enum import Enum
from pprint import pprint
from typing import Callable, Optional

from .. import builders, modeling, server
from ..tools.gui import modal_radiobutton_chooser
from .matplotlib import plot

graphql = server.run_graphql


class Materializers(Enum):
    NetworkX = (builders.NetworkxBuilder, plot)
    D3Graph = (builders.D3Builder, pprint)
    GraphQL = (builders.GraphQLBuilder, graphql)
    D3GraphQL = (builders.D3GraphQLBuilder, graphql)


def materialize(model: modeling.GraphModel,
                title: Optional[str] = None,
                graph_type: builders.GraphType = builders.GraphType.Graph,
                default_node_attributes: Optional[Mapping] = None,
                builder: Optional[type[builders.Builder]] = None,
                actualizer: Optional[Callable] = None,
                **kwargs):
    title = title or model.name
    if builder is None and actualizer is None:
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
