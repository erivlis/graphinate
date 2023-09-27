from . import builders
from .builders import GraphType, build
from .materializers import graphql, materialize, plot
from .modeling import UNIVERSE_NODE, GraphModel


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
