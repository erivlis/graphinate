from typing import Union, NamedTuple, Tuple, Any, Protocol, Iterable, TypeVar, FrozenSet, Mapping, Callable

Node = Union[type(NamedTuple), Tuple[str, Any]]
Edge = Union[type(NamedTuple), Tuple[str, str, Any]]
Element = Union[Node, Edge]
Extractor = Union[str, Callable[[Any], str]]

NodeTypeAbsoluteId = TypeVar("NodeTypeAbsoluteId", bound=Tuple[str, str])

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


ParametersId = FrozenSet


def parameters_id(mapping: Mapping) -> ParametersId:
    return frozenset(mapping.items())
