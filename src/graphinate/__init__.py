from . import builders
from .builders import GraphType, build
from .materializers import graphql, materialize, plot
from .modeling import UNIVERSE_NODE, GraphModel


def model(name: str):
    return GraphModel(name=name)
