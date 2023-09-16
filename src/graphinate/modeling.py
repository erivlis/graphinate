import inspect
from collections import defaultdict, namedtuple
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from .typing import Edge, Edges, Element, Extractor, Items, Node, Nodes, NodeTypeAbsoluteId

UNIVERSE_NODE = None


class GraphModelError(Exception):
    pass


def element(element_type: Optional[str], field_names: Optional[Iterable[str]] = None) -> Callable[[...], Element]:
    return namedtuple(element_type, field_names) if element_type and field_names else tuple


def extractor(obj: Any, key: Optional[Extractor] = None) -> Optional[str]:
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

    Parameters:
        iterable: source of payload
        element_type: Optional[Extractor] source of type of the element. Defaults to Element Type name.
        getters: Extractor node field sources

    Returns:
        Iterable of elements.
    """

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
    """Represents a Node Model

    Attributes:
        type: the type of the Node
        parent_type: the type of the node's parent
        uniqueness: is the Node universally unique
        parameters: parameters
        generator: Nodes generator method
        label: label source
    """

    type: str
    parent_type: Optional[str] = UNIVERSE_NODE
    uniqueness: bool = False
    parameters: Optional[set[str]] = None
    generator: Optional[Nodes] = None
    label: Callable[[Any], Optional[str]] = None

    @property
    def absolute_id(self) -> NodeTypeAbsoluteId:
        return self.parent_type, self.type


class GraphModel:
    """A Graph Model

       Used to declaratively register Edge and/or Node data supplier functions by using
       decorators.
    """
    def __init__(self, name: str):
        """Create a model for graph


        Parameters:
            name: the archetype name for Graphs generated based on the GraphModel.
        """
        self.name = name
        self._node_models: dict[NodeTypeAbsoluteId, NodeModel] = {}
        self._node_children: dict[str, list[str]] = defaultdict(list)
        self._edge_generators: dict[str, list[Edges]] = defaultdict(list)
        self._networkx_graph = None

    def __add__(self, other: 'GraphModel'):
        self._node_models.update(other._node_models)
        self._node_children.update(other._node_children)
        self._edge_generators.update(other._edge_generators)

    @property
    def node_models(self) -> dict[NodeTypeAbsoluteId, NodeModel]:
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
        return {v.type for v in self._node_models.values()}

    def node_children_types(self, _type: str = UNIVERSE_NODE) -> dict[str, list[str]]:
        """Children Node Types for given input Node Type

        Parameters:
            _type:  Node Type. Default value is UNIVERSE_NODE.

        Returns:
            List of children Node Types.
        """
        return {k: v for k, v in self._node_children.items() if k == _type}

    def _validate_node_parameters(self, parameters: list[str]):
        node_types = self.node_types
        if not all(p.endswith('_id') and p == p.lower() and p[:-3] in node_types for p in parameters):
            msg = ("Illegal Arguments. Argument should conform to the following rules: "
                   "1) lowercase "
                   "2) end with '_id' "
                   "3) start with value that exists as registered node type")

            raise GraphModelError(msg)

    def node(self,
             _type: Optional[Extractor] = None,
             parent_type: Optional[str] = UNIVERSE_NODE,
             uniqueness: bool = False,
             key: Optional[Extractor] = None,
             value: Optional[Extractor] = None,
             label: Optional[Extractor] = None) -> Callable[[Items], None]:
        """Decorator to Register a Generator of node payloads as a source to create Graph Nodes. It creates a
        NodeModel object.

        Parameters:
            _type: Optional source for the Node Type. Defaults to use Generator function
                   name as the Node Type.
            parent_type: Optional parent Node Type. Defaults to UNIVERSE_NODE
            uniqueness: Is the generated Node ID universally unique. Defaults to False.
            key: Optional source for Node IDs. Defaults to use the complete Node payload
                 as Node ID.
            value: Optional source for Node value field. Defaults to use the complete
                   Node payload as Node ID.
            label: Optional source for Node label field. Defaults to use a 'str'
                   representation of the complete Node payload.

        Returns:
            None
        """

        def register_node(f: Items):
            node_type = _type or f.__name__
            model_type = f.__name__ if callable(node_type) else node_type

            def node_generator(**kwargs) -> Iterable[Node]:
                yield from elements(f(**kwargs), node_type, key=key, value=value)

            parameters = inspect.getfullargspec(f).args
            node_model = NodeModel(type=model_type,
                                   parent_type=parent_type,
                                   uniqueness=uniqueness,
                                   parameters=set(parameters),
                                   label=label,
                                   generator=node_generator)
            self._node_models[node_model.absolute_id] = node_model
            self._node_children[parent_type].append(model_type)

            self._validate_node_parameters(parameters)

        return register_node

    def edge(self,
             _type: Optional[str] = None,
             source: Extractor = 'source',
             target: Extractor = 'target',
             label: Optional[Extractor] = str,
             value: Optional[Extractor] = None,
             weight: Union[float, Callable[[Any], float]] = 1.0,
             ) -> Callable[[Items], None]:
        """Decorator to Register a generator of edge payloads as a source to create
           Graph Edges. It creates an Edge generator function.

        Parameters:
            _type: Optional source for the Node Type. Defaults to use Generator function
                   name as the Node Type.
            source: Source for edge source Node ID.
            target: Source for edge target Node ID.
            label: Source for edge label.
            value: Source for edge value.
            weight: Source for edge weight.

        Returns:
            None.
        """

        def register_edge(f: Items):
            edge_type = _type or f.__name__

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

            self._edge_generators[edge_type].append(edge_generator)

        return register_edge

    def rectify(self, _type: Optional[Extractor] = None,
                parent_type: Optional[str] = UNIVERSE_NODE,
                key: Optional[Extractor] = None,
                value: Optional[Extractor] = None,
                label: Optional[Extractor] = None):
        if self._edge_generators and not self._node_models:
            @self.node(
                _type=_type or 'node',
                parent_type=parent_type or 'node',
                uniqueness=True,
                key=key,
                value=value,
                label=label or str
            )
            def node():
                return
                yield


__all__ = ('GraphModel', 'UNIVERSE_NODE')
