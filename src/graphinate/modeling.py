import inspect
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import Callable, Any, Iterable, Mapping, Set

from .typing import Node, Edge, Element, Items, Nodes, Edges, NodeTypeAbsoluteId

UNIVERSE_NODE = None


def element(element_type: str | None, field_names: Iterable[str] | None) -> Callable[[...], Element]:
    return namedtuple(element_type, field_names) if element_type and field_names else tuple


def extractor(obj: Any, key: str | Callable[[Any], str] | None = None) -> str | None:
    if key is None:
        return obj
    elif callable(key):
        return key(obj)
    elif isinstance(obj, Mapping) and isinstance(key, str):
        return obj.get(key, key)
    else:
        return key

    # return item if getter is None else (getter(item) if callable(getter) else getter)


def elements(iterable: Iterable[Any],
             element_type: str | None = None,
             **getters: str | Callable[[Any], str]) -> Iterable[Element]:
    create_element = element(element_type, getters.keys())
    for item in iterable:
        kwargs = {k: extractor(item, v) for k, v in getters.items()}
        yield create_element(**kwargs)


@dataclass
class NodeModel:
    """
    Represents a node model
    Attributes:
        type
        parent_type
        uniqueness
        parameters
        generator
    """
    type: str
    parent_type: str | None = UNIVERSE_NODE
    uniqueness: bool = False
    parameters: Set[str] | None = None
    generator: Nodes | None = None
    label: Callable[[Any], str | None] = None

    @property
    def absolute_id(self) -> NodeTypeAbsoluteId:
        return self.parent_type, self.type


class GraphModel:

    def __init__(self, name: str):
        self.name = name
        self._node_models: dict[NodeTypeAbsoluteId, NodeModel] = {}
        self._nodes_children: dict[str, list[str]] = defaultdict(list)
        self._edges_generators: dict[str, list[Edges]] = defaultdict(list)
        self._networkx_graph = None

    @property
    def node_models(self):
        return self._node_models

    @property
    def edges_generators(self):
        return self._edges_generators

    @property
    def types(self) -> Set:
        return {v.type for v in self._node_models.values()}

    def node_children(self, type: str = UNIVERSE_NODE) -> dict[str, list[str]]:
        return {k: v for k, v in self._nodes_children.items() if k == type}

    def _verify_parameters(self, parameters):
        assert True

    def node(self,
             _type: str | None = None,
             parent_type: str | None = UNIVERSE_NODE,
             uniqueness: bool = False,
             key: str | Callable[[Any], str] | None = None,
             value: str | Callable[[Any], str] | None = None,
             label: str | Callable[[Any], str] | None = None) -> Callable[[Items], None]:
        def register(f: Items):
            node_type = _type or f.__name__

            def node_generator(**kwargs) -> Iterable[Node]:
                yield from elements(f(**kwargs), node_type, key=key, value=value)

            parameters = inspect.getfullargspec(f).args
            self._verify_parameters(parameters)

            node_model = NodeModel(type=node_type,
                                   parent_type=parent_type,
                                   uniqueness=uniqueness,
                                   parameters=set(parameters),
                                   label=label,
                                   generator=node_generator)
            self._node_models[node_model.absolute_id] = node_model
            self._nodes_children[parent_type].append(node_type)
            # self._nodes_parents[node_type].append(parent_node_type)

        return register

    def edge(self,
             _type: str | None = None,
             source: str | Callable[[Any], str] = 'source',
             target: str | Callable[[Any], str] = 'target',
             label: str | Callable[[Any], str] | None = None,
             value: str | Callable[[Any], str] | None = None,
             weight: float | Callable[[Any], float] = 1.0,
             ) -> Callable[[Items], None]:
        def register(f: Items):
            edge_type = _type or f.__name__

            getters = {
                'source': source,
                'target': target,
                'label': label,
                'value': value,
                'weight': weight
            }

            def edge_generator(**kwargs) -> Iterable[Edge]:
                yield from elements(f(**kwargs), edge_type, **getters)

            self._edges_generators[edge_type].append(edge_generator)

        return register


__all__ = ('GraphModel', 'UNIVERSE_NODE')
