import inspect
import itertools
from collections import defaultdict, namedtuple
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional, Union

from .typing import Edge, Element, Extractor, Items, Node, NodeTypeAbsoluteId, UniverseNode


class GraphModelError(Exception):
    pass


def element(element_type: Optional[str], field_names: Optional[Iterable[str]] = None) -> Callable[[...], Element]:
    """Graph Element Supplier Callable

    Args:
        element_type:
        field_names:

    Returns:
        Element Supplier Callable
    """
    return namedtuple(element_type, field_names) if element_type and field_names else tuple


def extractor(obj: Any, key: Optional[Extractor] = None) -> Optional[str]:
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
             element_type: Optional[Extractor] = None,
             **getters: Extractor) -> Iterable[Element]:
    """Abstract Generator of Graph elements (nodes or edges)

    Args:
        iterable: source of payload
        element_type: Optional[Extractor] source of type of the element. Defaults to Element Type name.
        getters: Extractor node field sources

    Returns:
        Iterable of Elements.
    """
    for item in iterable:
        _type = element_type(item) if element_type and callable(element_type) else element_type
        if not _type.isidentifier():
            raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")

        create_element = element(_type, getters.keys())
        kwargs = {k: extractor(item, v) for k, v in getters.items()}
        yield create_element(**kwargs)


class Multiplicity(Enum):
    ADD = auto()
    ALL = auto()
    FIRST = auto()
    LAST = auto()


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
    parent_type: Optional[str] = UniverseNode
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
        self._node_children: dict[str, list[str]] = defaultdict(list)
        self._edge_generators: dict[str, list[Callable[[], Iterable[Edge]]]] = defaultdict(list)
        self._networkx_graph = None

    def __add__(self, other: 'GraphModel'):
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
    def node_models(self) -> dict[NodeTypeAbsoluteId, list[NodeModel]]:
        """
        Returns:
            NodeModel for Node Types. Key values are NodeTypeAbsoluteId.
        """
        return self._node_models

    @property
    def edge_generators(self):
        """
        Returns:
            Edge generator functions for Edge Types
        """
        return self._edge_generators

    @property
    def node_types(self) -> set[str]:
        """
        Returns:
            Node Types
        """
        return {v.type for v in itertools.chain.from_iterable(self._node_models.values())}

    def node_children_types(self, _type: str = UniverseNode) -> dict[str, list[str]]:
        """Children Node Types for given input Node Type

        Args:
            _type:  Node Type. Default value is UNIVERSE_NODE.

        Returns:
            List of children Node Types.
        """
        return {k: v for k, v in self._node_children.items() if k == _type}

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
             type_: Optional[Extractor] = None,
             parent_type: Optional[str] = UniverseNode,
             key: Optional[Extractor] = None,
             value: Optional[Extractor] = None,
             label: Optional[Extractor] = None,
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

        Returns:
            None
        """

        def register_node(f: Items):
            node_type = type_ or f.__name__
            self._validate_type(node_type)

            model_type = f.__name__ if callable(node_type) else node_type

            def node_generator(**kwargs) -> Iterable[Node]:
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
             type_: Optional[Extractor] = None,
             source: Extractor = 'source',
             target: Extractor = 'target',
             label: Optional[Extractor] = str,
             value: Optional[Extractor] = None,
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

            def edge_generator(**kwargs) -> Iterable[Edge]:
                yield from elements(f(**kwargs), edge_type, **getters)

            self._edge_generators[model_type].append(edge_generator)

        return register_edge

    def rectify(self, _type: Optional[Extractor] = None,
                parent_type: Optional[str] = UniverseNode,
                key: Optional[Extractor] = None,
                value: Optional[Extractor] = None,
                label: Optional[Extractor] = None):
        """Rectify the model.
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
    """Create a graph model

    Args:
        name: model name

    Returns:
        GraphModel
    """
    return GraphModel(name=name)


__all__ = ('GraphModel', 'Multiplicity', 'model')
