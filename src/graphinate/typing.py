"""Typing Module

  Attributes:
    Node (Node): Node Type
    Edge (Edge): Edge Type
    Element (Element): Element Type
    Extractor (Extractor): Source of data for an Element
"""

from collections.abc import Iterable
from typing import Any, Callable, NamedTuple, Protocol, TypeVar, Union

Node = Union[type[NamedTuple], tuple[str, Any]]

Edge = Union[type[NamedTuple], tuple[str, str, Any]]

Element = Union[Node, Edge]

Extractor = Union[str, Callable[[Any], str]]

NodeTypeAbsoluteId = TypeVar("NodeTypeAbsoluteId", bound=tuple[str, str])

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
