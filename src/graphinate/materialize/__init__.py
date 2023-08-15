from collections.abc import Mapping
from enum import Enum
from pprint import pprint
from typing import Callable, Optional

from .. import builders, modeling, server
from ..tools.gui import modal_radiobutton_chooser
from .matplotlib import show


class Materializers(Enum):
    NetworkX = (builders.NetworkxBuilder, show)
    D3Graph = (builders.D3Builder, pprint)
    GraphQL = (builders.GraphQLBuilder, server.run_graphql)
    D3GraphQL = (builders.D3GraphQLBuilder, server.run_graphql)


def materialize(title: str,
                graph_model: modeling.GraphModel,
                graph_type: builders.GraphType = builders.GraphType.Graph,
                default_node_attributes: Optional[Mapping] = None,
                builder: Optional[type[builders.Builder]] = None,
                actualizer: Optional[Callable] = None,
                **kwargs):
    if builder is None and actualizer is None:
        result = modal_radiobutton_chooser(title,
                                           options={m.name: m.value for m in Materializers},
                                           default=(None, None))
        if result[0]:
            builder, actualizer = result[1]

    materialized_graph = builders.build(builder,
                                        graph_model,
                                        graph_type,
                                        default_node_attributes=default_node_attributes,
                                        **kwargs)
    actualizer(materialized_graph)
