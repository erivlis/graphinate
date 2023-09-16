"""
Typing module

Attributes:
    Node (Node): Node payload Type
    Edge (Edge): Edge payload Type
    Element (Element): Element Type
    Extractor (Extractor): Source of data for an Element
"""


from collections.abc import Iterable, Mapping
from typing import Any, Callable, NamedTuple, Protocol, TypeVar, Union

Node = Union[type(NamedTuple), tuple[str, Any]]
Edge = Union[type(NamedTuple), tuple[str, str, Any]]
Element = Union[Node, Edge]


Extractor = Union[str, Callable[[Any], str]]

NodeTypeAbsoluteId = TypeVar("NodeTypeAbsoluteId", bound=tuple[str, str])

T = TypeVar("T")


class Items(Protocol):
    def __call__(self, **kwargs) -> Iterable[T]:
        ...


class Nodes(Protocol):
    def __call__(self, **kwargs) -> Iterable[Node]:
        ...


class Edges(Protocol):
    def __call__(self, **kwargs) -> Iterable[Edge]:
        ...


class Predicate(Protocol):
    def __call__(self, **kwargs) -> bool:
        ...


class Supplier(Protocol):
    def __call__(self) -> Any:
        ...


ParametersId = frozenset


def parameters_id(mapping: Mapping) -> ParametersId:
    return frozenset(mapping.items())
