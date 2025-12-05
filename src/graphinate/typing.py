"""
Typing Module

Attributes:
  Node (Node): Node Type
  Edge (Edge): Edge Type
  Element (Element): Element Type
  Extractor (Extractor): Source of data for an Element
  UniverseNode (UniverseNode): The Universe Node Type. All Node Types are the implicit children of UniverseNodeType.
"""

from collections.abc import Callable, Iterable
from typing import Any, NamedTuple, NewType, Protocol, TypeAlias, TypeVar, Union

import networkx as nx
import networkx_mermaid as nxm
import strawberry

NodeTuple: TypeAlias = tuple[str, Any]
EdgeTuple: TypeAlias = tuple[str, str, Any]

IdentifierStr = NewType('IdentifierStr', str)
IdentifierStr.__doc__ = 'A string that is a valid Python identifier (i.e., `isidentifier()` is True).'

NodeTypeAbsoluteId = NewType('NodeTypeAbsoluteId', tuple[str, str])
NodeTypeAbsoluteId.__doc__ = 'A unique identifier for a node type.'


class UniverseNode:
    """The UniverseNode Type. All Node Types are the implicit children of the Universe Node Type."""


# A node in a graph.
Node = Union[type[NamedTuple], NodeTuple]  # noqa: UP007

# An edge in a graph.
Edge = Union[type[NamedTuple], EdgeTuple]  # noqa: UP007

# An element in a graph.
Element = Union[Node, Edge]  # noqa: UP007

# A source of data for an element.
Extractor = Union[str, Callable[[Any], str]]  # noqa: UP007

T = TypeVar('T')


class Items(Protocol):
    """Protocol for callable objects that return an iterable of items."""

    def __call__(self, **kwargs: Any) -> Iterable[T]:  # pragma: no cover
        ...


class Nodes(Protocol):
    """Protocol for callable objects that return an iterable of nodes."""

    def __call__(self, **kwargs: Any) -> Iterable[Node]:  # pragma: no cover
        ...


class Edges(Protocol):
    """Protocol for callable objects that return an iterable of edges."""

    def __call__(self, **kwargs: Any) -> Iterable[Edge]:  # pragma: no cover
        ...


class Predicate(Protocol):
    """Protocol for callable objects that evaluate a condition."""

    def __call__(self, **kwargs: Any) -> bool:  # pragma: no cover
        ...


class Supplier(Protocol):
    """Protocol for callable objects that supply a value."""

    def __call__(self) -> Any:  # pragma: no cover
        ...


GraphRepresentation = Union[dict, nx.Graph, strawberry.Schema, nxm.typing.MermaidDiagram, str]  # noqa: UP007
