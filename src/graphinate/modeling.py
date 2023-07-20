import inspect
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import Callable, Any, Iterable, Mapping, Set, Optional, Union

from .typing import Node, Edge, Element, Items, Nodes, Edges, NodeTypeAbsoluteId, Extractor

UNIVERSE_NODE = None


def element(element_type: Optional[str], field_names: Optional[Iterable[str]] = None) -> Callable[[...], Element]:
    return namedtuple(element_type, field_names) if element_type and field_names else tuple


def extractor(obj: Any, key: Optional[Extractor] = None) -> Optional[str]:
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
             element_type: Optional[Extractor] = None,
             **getters: Extractor) -> Iterable[Element]:
    if callable(element_type):
        for item in iterable:
            create_element = element(element_type(item), getters.keys())
            kwargs = {k: extractor(item, v) for k, v in getters.items()}
            yield create_element(**kwargs)
    else:
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
    parent_type: Optional[str] = UNIVERSE_NODE
    uniqueness: bool = False
    parameters: Optional[Set[str]] = None
    generator: Optional[Nodes] = None
    label: Callable[[Any], Optional[str]] = None

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
        return True

    def node(self,
             _type: Optional[Extractor] = None,
             parent_type: Optional[str] = UNIVERSE_NODE,
             uniqueness: bool = False,
             key: Optional[Extractor] = None,
             value: Optional[Extractor] = None,
             label: Optional[Extractor] = None) -> Callable[[Items], None]:
        def register(f: Items):
            node_type = _type or f.__name__
            model_type = f.__name__ if callable(node_type) else node_type

            def node_generator(**kwargs) -> Iterable[Node]:
                yield from elements(f(**kwargs), node_type, key=key, value=value)

            parameters = inspect.getfullargspec(f).args
            self._verify_parameters(parameters)

            node_model = NodeModel(type=model_type,
                                   parent_type=parent_type,
                                   uniqueness=uniqueness,
                                   parameters=set(parameters),
                                   label=label,
                                   generator=node_generator)
            self._node_models[node_model.absolute_id] = node_model
            self._nodes_children[parent_type].append(model_type)
            # self._nodes_parents[node_type].append(parent_node_type)

        return register

    def edge(self,
             _type: Optional[str] = None,
             source: Extractor = 'source',
             target: Extractor = 'target',
             label: Optional[Extractor] = None,
             value: Optional[Extractor] = None,
             weight: Union[float, Callable[[Any], float]] = 1.0,
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
