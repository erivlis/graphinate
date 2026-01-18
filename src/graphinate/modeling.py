import inspect
import itertools
from collections import defaultdict, namedtuple
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Any, Union

from .enums import Multiplicity
from .typing import Edge, Element, Extractor, Items, Node, NodeTypeAbsoluteId, UniverseNode


class GraphModelError(Exception):
    pass


@lru_cache(maxsize=128)
def _get_namedtuple_element_class(type_name: str, field_names: tuple[str] | str) -> type[Element]:
    return namedtuple(type_name, field_names)


def element(element_type: str | None, field_names: Iterable[str] | str | None = None) -> Callable[[], Element]:
    """Graph Element Supplier Callable

    Args:
        element_type:
        field_names:

    Returns:
        Element Supplier Callable
    """

    if not isinstance(field_names, str):
        field_names = tuple(field_names)

    return _get_namedtuple_element_class(element_type, field_names) if element_type and field_names else tuple


def extractor(obj: Any, key: Extractor | None = None) -> str | None:
    """Extract data item from Element

    Args:
        obj:
        key:

    Returns:
        Element data item
    """
    if key is None:
        return obj

    if callable(key):
        return key(obj)

    if isinstance(obj, Mapping) and isinstance(key, str):
        return obj.get(key, key)

    return key


def elements(iterable: Iterable[Any],
             element_type: Extractor | None = None,
             **getters: Extractor) -> Iterable[Element]:
    """Abstract Generator of Graph elements (nodes or edges)

    Args:
        iterable: source of payload
        element_type: Optional[Extractor] source of type of the element. Defaults to Element Type name.
        getters: Extractor node field sources

    Returns:
        Iterable of Elements.
    """
    is_dynamic_type = callable(element_type)
    static_create_element = None

    if not is_dynamic_type:
        _type = element_type
        # Eagerly validate static types.
        # Note: This will raise AttributeError if _type is None (consistent with previous behavior, but happens earlier)
        # and ValueError if _type is invalid identifier.
        if not _type.isidentifier():
            raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")

        static_create_element = element(_type, getters.keys())

    for item in iterable:
        if is_dynamic_type:
            _type = element_type(item)
            if not _type.isidentifier():
                raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")
            create_element = element(_type, getters.keys())
        else:
            create_element = static_create_element

        kwargs = {k: extractor(item, v) for k, v in getters.items()}
        yield create_element(**kwargs)


@dataclass
class NodeModel:
    """Represents a Node Model

    Args:
        type: the type of the Node.
        parent_type: the type of the node's parent. Defaults to UniverseNode.
        parameters: parameters of the Node. Defaults to None.
        label: label source. Defaults to None.
        uniqueness: is the Node universally unique. Defaults to True.
        multiplicity: Multiplicity of the Node. Defaults to ALL.
        generator: Nodes generator method. Defaults to None.

    Properties:
        absolute_id: return the NodeModel absolute_id.
    """

    type: str
    parent_type: str | UniverseNode | None = UniverseNode
    parameters: set[str] | None = None
    label: Callable[[Any], str | None] = None
    uniqueness: bool = True
    multiplicity: Multiplicity = Multiplicity.ALL
    generator: Callable[[], Iterable[Node]] | None = None

    @property
    def absolute_id(self) -> NodeTypeAbsoluteId:
        return self.parent_type, self.type


class GraphModel:
    """A Graph Model

    Used to declaratively register Edge and/or Node data supplier functions by using
    decorators.

    Args:
        name: the archetype name for Graphs generated based on the GraphModel.
    """

    def __init__(self, name: str):
        self.name: str = name
        self._node_models: dict[NodeTypeAbsoluteId, list[NodeModel]] = defaultdict(list)
        self._node_children: dict[str, list[NodeModel]] = defaultdict(list)
        self._edge_generators: dict[str, list[Callable[[], Iterable[Edge]]]] = defaultdict(list)
        self._networkx_graph = None

    def __add__(self, other: 'GraphModel') -> 'GraphModel':
        graph_model = GraphModel(name=f"{self.name} + {other.name}")
        for m in (self, other):
            for k, v in m._node_models.items():
                graph_model._node_models[k].extend(v)

            for k, v in m._node_children.items():
                graph_model._node_children[k].extend(v)

            for k, v in m._edge_generators.items():
                graph_model._edge_generators[k].extend(v)

        return graph_model

    @property
    def node_models(self) -> Mapping[NodeTypeAbsoluteId, list[NodeModel]]:
        """
        Returns:
            NodeModel for Node Types. Key values are NodeTypeAbsoluteId.
        """
        return MappingProxyType(self._node_models)

    @property
    def edge_generators(self) -> Mapping[str, list[Callable[[], Iterable[Edge]]]]:
        """
        Returns:
            Edge generator functions for Edge Types
        """
        return MappingProxyType(self._edge_generators)

    @property
    def node_types(self) -> set[str]:
        """
        Returns:
            Node Types
        """
        return {v.type for v in itertools.chain.from_iterable(self._node_models.values())}

    def node_children_types(self, _type: str = UniverseNode) -> Mapping[str, list[str]]:
        """Children Node Types for given input Node Type

        Args:
            _type:  Node Type. Default value is UNIVERSE_NODE.

        Returns:
            List of children Node Types.
        """
        return MappingProxyType({k: v for k, v in self._node_children.items() if k == _type})

    @staticmethod
    def _validate_type(node_type: str):
        if not callable(node_type) and not node_type.isidentifier():
            raise ValueError(f"Invalid Type: {node_type}. Must be a valid Python identifier.")

    def _validate_node_parameters(self, parameters: list[str]):
        node_types = self.node_types
        if not all(p.endswith('_id') and p == p.lower() and p[:-3] in node_types for p in parameters):
            msg = ("Illegal Arguments. Argument should conform to the following rules: "
                   "1) lowercase "
                   "2) end with '_id' "
                   "3) start with value that exists as registered node type")

            raise GraphModelError(msg)

    def node(self,
             type_: Extractor | None = None,
             parent_type: str | None = UniverseNode,
             key: Extractor | None = None,
             value: Extractor | None = None,
             label: Extractor | None = None,
             unique: bool = True,
             multiplicity: Multiplicity = Multiplicity.ALL) -> Callable[[Items], None]:
        """Decorator to Register a Generator of node payloads as a source for Graph Nodes.
        It creates a NodeModel object.

        Args:
            type_: Optional source for the Node Type. Defaults to use Generator function
                   name as the Node Type.
            parent_type: Optional parent Node Type. Defaults to UNIVERSE_NODE

            key: Optional source for Node IDs. Defaults to use the complete Node payload
                 as Node ID.
            value: Optional source for Node value field. Defaults to use the complete
                   Node payload as Node ID.
            label: Optional source for Node label field. Defaults to use a 'str'
                   representation of the complete Node payload.
            unique: is the Node universally unique. Defaults to True.
            multiplicity: Multiplicity of the Node. Defaults to ALL.

        Generator Function Signature:
            The decorated generator function may accept arguments to receive context from parent nodes.
            These arguments MUST conform to the following strict naming convention:
            1. The argument name must be lowercase.
            2. The argument name must end with '_id'.
            3. The prefix (before '_id') must match an existing registered Node Type.

            Example:
                If you have a parent node type 'user', your child node generator can accept 'user_id'.

                @model.node(parent_type='user')
                def get_posts(user_id): ...

            Note: Arbitrary arguments (e.g., configuration flags) are currently NOT supported.

        Returns:
            None
        """

        def register_node(f: Items):
            node_type = type_ or f.__name__
            self._validate_type(node_type)

            model_type = f.__name__ if callable(node_type) else node_type

            def node_generator(**kwargs: Any) -> Iterable[Node]:
                yield from elements(f(**kwargs), node_type, key=key, value=value)

            parameters = inspect.getfullargspec(f).args
            node_model = NodeModel(type=model_type,
                                   parent_type=parent_type,
                                   parameters=set(parameters),
                                   label=label,
                                   uniqueness=unique,
                                   multiplicity=multiplicity,
                                   generator=node_generator)
            self._node_models[node_model.absolute_id].append(node_model)
            self._node_children[parent_type].append(model_type)

            self._validate_node_parameters(parameters)

        return register_node

    def edge(self,
             type_: Extractor | None = None,
             source: Extractor = 'source',
             target: Extractor = 'target',
             label: Extractor | None = str,
             value: Extractor | None = None,
             weight: Union[float, Callable[[Any], float]] = 1.0,
             ) -> Callable[[Items], None]:
        """Decorator to Register a generator of edge payloads as a source of Graph Edges.
         It creates an Edge generator function.

        Args:
            type_: Optional source for the Edge Type. Defaults to use Generator function
                   name as the Edge Type.
            source: Source for edge source Node ID.
            target: Source for edge target Node ID.
            label: Source for edge label.
            value: Source for edge value.
            weight: Source for edge weight.

        Returns:
            None.
        """

        def register_edge(f: Items):
            edge_type = type_ or f.__name__
            self._validate_type(edge_type)

            model_type = f.__name__ if callable(edge_type) else edge_type

            getters = {
                'source': source,
                'target': target,
                'label': label,
                'type': edge_type,
                'value': value,
                'weight': weight
            }

            def edge_generator(**kwargs: Any) -> Iterable[Edge]:
                yield from elements(f(**kwargs), edge_type, **getters)

            self._edge_generators[model_type].append(edge_generator)

        return register_edge

    def rectify(self, _type: Extractor | None = None,
                parent_type: str | None = UniverseNode,
                key: Extractor | None = None,
                value: Extractor | None = None,
                label: Extractor | None = None):
        """
        Rectify the model.
        Add a default NodeModel in case of having just edge supplier/s and no node supplier/s.

       Args:
           _type
           parent_type
           key
           value
           label

       Returns:
           None
        """
        if self._edge_generators and not self._node_models:
            @self.node(
                type_=_type or 'node',
                parent_type=parent_type or 'node',
                unique=True,
                key=key,
                value=value,
                label=label or str
            )
            def node():  # pragma: no cover
                return
                yield


def model(name: str):
    """
    Create a graph model

    Args:
        name: model name

    Returns:
        GraphModel
    """
    return GraphModel(name=name)


__all__ = ('GraphModel', 'model', 'elements')
