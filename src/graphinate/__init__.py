from graphinate import builders
from graphinate.builders import GraphType, build
from graphinate.materializers import materialize, plot
from graphinate.modeling import UNIVERSE_NODE, GraphModel
from graphinate.server import graphql


def model(name: str):
    """Create a graph model

    Args:
        name:

    Returns:
        GraphModel
    """
    return GraphModel(name=name)


__all__ = (
    'build',
    'builders',
    'GraphModel',
    'graphql',
    'GraphType',
    'materialize',
    'model',
    'plot',
    'UNIVERSE_NODE'
)
