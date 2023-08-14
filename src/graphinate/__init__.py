from . import builders
from .builders import GraphType
from .materialize import materialize
from .modeling import UNIVERSE_NODE, GraphModel


def model(name: str):
    return GraphModel(name=name)
