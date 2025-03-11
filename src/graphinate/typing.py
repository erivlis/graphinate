"""Typing Module

  Attributes:
      Node (Node): Node Type
      Edge (Edge): Edge Type
      Element (Element): Element Type
      Extractor (Extractor): Source of data for an Element
"""

from collections.abc import Callable, Iterable
from typing import Any, NamedTuple, NewType, Protocol, TypeVar, Union

IdentifierStr = NewType('IdentifierStr', str)
IdentifierStr.__doc__ = "A string that is a valid Python identifier (i.e., `isidentifier()` is True)."

NodeTypeAbsoluteId = NewType("NodeTypeAbsoluteId", tuple[str, str])
NodeTypeAbsoluteId.__doc__ = "A unique identifier for a node type."

UniverseNode = NewType('UniverseNode', None)
UniverseNode.__doc__ = "The UniverseNode Type. All Node Types are the implicit children of the Universe Node Type."

Node = Union[type[NamedTuple], tuple[str, Any]]  # noqa: UP007
Node.__doc__ = "A node in a graph."

Edge = Union[type[NamedTuple], tuple[str, str, Any]]  # noqa: UP007
Edge.__doc__ = "An edge in a graph."

Element = Union[Node, Edge]  # noqa: UP007
Element.__doc__ = "An element in a graph."

Extractor = Union[str, Callable[[Any], str]]  # noqa: UP007
Extractor.__doc__ = "A source of data for an element."

T = TypeVar("T")


class Items(Protocol):
    def __call__(self, **kwargs) -> Iterable[T]:
        ...  # pragma: no cover


class Nodes(Protocol):
    def __call__(self, **kwargs) -> Iterable[Node]:
        ...  # pragma: no cover


class Edges(Protocol):
    def __call__(self, **kwargs) -> Iterable[Edge]:
        ...  # pragma: no cover


class Predicate(Protocol):
    def __call__(self, **kwargs) -> bool:
        ...  # pragma: no cover


class Supplier(Protocol):
    def __call__(self) -> Any:
        ...  # pragma: no cover

# ParametersId = frozenset


# def parameters_id(mapping: Mapping) -> ParametersId:
#     return frozenset(mapping.items())
