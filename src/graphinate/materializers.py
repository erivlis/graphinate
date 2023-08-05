from pprint import pprint
from typing import Mapping, Optional

from . import builders, server
from .modeling import GraphModel
from .tools.gui import modal_radiobutton_chooser
from .visualizers import show

output_modes = {
    'NetworkX': (builders.NetworkxBuilder, show),
    'D3 Graph': (builders.D3Builder, pprint),
    'GraphQL': (builders.GraphQLBuilder, server.run_graphql),
    'D3 GraphQL': (builders.D3GraphQLBuilder, server.run_graphql)
}


def materialize(title: str,
                graph_model: GraphModel,
                graph_type: builders.GraphType = builders.GraphType.Graph,
                default_node_attributes: Optional[Mapping] = None,
                **kwargs):
    result = modal_radiobutton_chooser(title, options=output_modes, default=(None, None))
    if result[0]:
        builder, show = result[1]
        if builder:
            materialized_graph = builders.build(builder,
                                                graph_model,
                                                graph_type,
                                                default_node_attributes=default_node_attributes,
                                                **kwargs)
            show(materialized_graph)
