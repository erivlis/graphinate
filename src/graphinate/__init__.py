from . import builders
from .builders import GraphType
from .materialize import materialize
from .modeling import GraphModel, UNIVERSE_NODE


def model(name: str):
    return GraphModel(name=name)
