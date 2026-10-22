import inspect
import itertools
import typing
from collections import defaultdict, namedtuple
from collections.abc import AsyncIterable, Callable, Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Any, Union

from .enums import CompositionStrategy, Multiplicity
from .typing import Edge, Element, Extractor, Items, Node, NodeTypeAbsoluteId, ParentId, UniverseNode


class GraphModelError(Exception):
    pass


@lru_cache(maxsize=128)
def _get_namedtuple_element_class(type_name: str, field_names: tuple[str, ...] | str) -> type[Element]:
    return namedtuple(type_name, field_names)


def tuple_element() -> type[tuple]:
    """Return the standard tuple element factory.

    Returns:
        The built-in `tuple` constructor.
    """
    return tuple


def named_element(element_type: str, field_names: Iterable[str] | str) -> type[Element]:
    """Return a named tuple element factory for the given type and field names.

    Args:
        element_type: Valid Python identifier for the named tuple class name.
        field_names: Field names as an iterable of strings or space/comma-separated string.

    Returns:
        A cached namedtuple class for the specified type and fields.

    Raises:
        ValueError: If element_type is empty/invalid or field_names is empty.
    """
    if not element_type or not isinstance(element_type, str) or not element_type.isidentifier():
        raise ValueError(f"Invalid Type: {element_type}. Must be a valid Python identifier.")

    if not isinstance(field_names, str):
        field_names = tuple(field_names)

    if not field_names:
        raise ValueError("field_names must not be empty for named_element.")

    return _get_namedtuple_element_class(element_type, field_names)


def element(element_type: str | None, field_names: Iterable[str] | str | None = None) -> Callable[..., Element]:
    """Graph Element Supplier Callable

    Args:
        element_type:
        field_names:

    Returns:
        Element Supplier Callable
    """
    if field_names is not None and not isinstance(field_names, str):
        field_names = tuple(field_names)

    if element_type and field_names:
        return named_element(element_type, field_names)
    return tuple_element()


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
    field_names = tuple(getters.keys())

    if not is_dynamic_type:
        _type = element_type
        # Eagerly validate static types.
        # Note: This will raise AttributeError if _type is None (consistent with previous behavior, but happens earlier)
        # and ValueError if _type is invalid identifier.
        if not _type.isidentifier():
            raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")

        static_create_element = named_element(_type, field_names) if field_names else tuple_element()

    for item in iterable:
        if is_dynamic_type:
            _type = element_type(item)
            if not _type.isidentifier():
                raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")
            create_element = named_element(_type, field_names) if field_names else tuple_element()
        else:
            create_element = static_create_element

        kwargs = {k: extractor(item, v) for k, v in getters.items()}
        yield create_element(**kwargs) if field_names else create_element()


async def aelements(
    iterable: AsyncIterable[Any] | Iterable[Any],
    element_type: Extractor | None = None,
    **getters: Extractor,
) -> AsyncIterable[Element]:
    """Asynchronous Generator of Graph elements (nodes or edges).

    Args:
        iterable: async or sync source of payload
        element_type: Optional[Extractor] source of type of the element.
        getters: Extractor node field sources

    Yields:
        Element instances.
    """
    is_dynamic_type = callable(element_type)
    static_create_element = None
    field_names = tuple(getters.keys())

    if not is_dynamic_type:
        _type = element_type
        if not _type.isidentifier():
            raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")
        static_create_element = named_element(_type, field_names) if field_names else tuple_element()

    if isinstance(iterable, AsyncIterable):
        async for item in iterable:
            if is_dynamic_type:
                _type = element_type(item)
                if not _type.isidentifier():
                    raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")
                create_element = named_element(_type, field_names) if field_names else tuple_element()
            else:
                create_element = static_create_element

            kwargs = {k: extractor(item, v) for k, v in getters.items()}
            yield create_element(**kwargs) if field_names else create_element()
    else:
        for item in iterable:
            if is_dynamic_type:
                _type = element_type(item)
                if not _type.isidentifier():
                    raise ValueError(f"Invalid Type: {_type}. Must be a valid Python identifier.")
                create_element = named_element(_type, field_names) if field_names else tuple_element()
            else:
                create_element = static_create_element

            kwargs = {k: extractor(item, v) for k, v in getters.items()}
            yield create_element(**kwargs) if field_names else create_element()


@dataclass
class NodeModel:
    """Represents a Node Model

    Args:
        type: the type of the Node.
        parent_type: the type of the node's parent. Defaults to UniverseNode.
        label: label source. Defaults to None.
        uniqueness: is the Node universally unique. Defaults to True.
        multiplicity: Multiplicity of the Node. Defaults to ALL.
        dependencies: Node type dependencies. Defaults to None.
        generator: Nodes type generator method. Defaults to None.
        dynamic_type: Whether the node type is resolved dynamically at runtime via a callable. Defaults to False.

    Properties:
        absolute_id: return the NodeModel absolute_id.
    """
    type: str
    parent_type: str | UniverseNode | None = UniverseNode
    label: Callable[[Any], str | None] = None
    uniqueness: bool = True
    multiplicity: Multiplicity = Multiplicity.ALL
    dependencies: dict[str, str] | None = None
    generator: Callable[[], Iterable[Node]] | None = None
    dynamic_type: bool = False


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

    def _check_merge_conflicts(self, other: 'GraphModel'):
        overlapping_nodes = set(self._node_models.keys()) & set(other._node_models.keys())
        overlapping_edges = set(self._edge_generators.keys()) & set(other._edge_generators.keys())
        if overlapping_nodes or overlapping_edges:
            conflicts = []
            if overlapping_nodes:
                conflicts.append(f"node types {sorted(str(k) for k in overlapping_nodes)}")
            if overlapping_edges:
                conflicts.append(f"edge types {sorted(overlapping_edges)}")
            raise GraphModelError(
                f"Model composition conflict under FAIL strategy: overlapping {', '.join(conflicts)}."
            )

    def _merge_append(self, other: 'GraphModel', target: 'GraphModel'):
        for m in (self, other):
            for k, v in m._node_models.items():
                target._node_models[k].extend(v)
            for k, v in m._node_children.items():
                target._node_children[k].extend(v)
            for k, v in m._edge_generators.items():
                target._edge_generators[k].extend(v)

    def _merge_override(self, other: 'GraphModel', target: 'GraphModel'):
        for m in (self, other):
            for k, v in m._node_models.items():
                target._node_models[k] = list(v)
            for k, v in m._edge_generators.items():
                target._edge_generators[k] = list(v)

        for (parent_type, _), models in target._node_models.items():
            for nm in models:
                target._node_children[parent_type].append(nm.type)

    @staticmethod
    def _merge_node_model_lists(left_models: list[NodeModel], right_models: list[NodeModel]) -> list[NodeModel]:
        if not right_models:
            return list(left_models)
        right_primary = right_models[-1]
        merged = []
        for existing in left_models:
            merged_deps = {**(existing.dependencies or {}), **(right_primary.dependencies or {})}
            merged.append(
                NodeModel(
                    type=right_primary.type,
                    parent_type=right_primary.parent_type,
                    label=right_primary.label if right_primary.label is not None else existing.label,
                    uniqueness=right_primary.uniqueness,
                    multiplicity=right_primary.multiplicity,
                    dependencies=merged_deps,
                    generator=existing.generator,
                    dynamic_type=existing.dynamic_type,
                )
            )
        seen_generators = {nm.generator for nm in merged}
        for nm in right_models:
            if nm.generator not in seen_generators:
                merged.append(nm)
                seen_generators.add(nm.generator)
        return merged

    def _merge_combine(self, other: 'GraphModel', target: 'GraphModel'):
        for k, v in self._node_models.items():
            target._node_models[k] = list(v)
        for k, v in other._node_models.items():
            if k in target._node_models:
                target._node_models[k] = self._merge_node_model_lists(target._node_models[k], v)
            else:
                target._node_models[k] = list(v)

        for (parent_type, _), models in target._node_models.items():
            for nm in models:
                if nm.type not in target._node_children[parent_type]:
                    target._node_children[parent_type].append(nm.type)

        for m in (self, other):
            for k, v in m._edge_generators.items():
                for gen in v:
                    if gen not in target._edge_generators[k]:
                        target._edge_generators[k].append(gen)

    def merge(
        self,
        other: 'GraphModel',
        strategy: CompositionStrategy = CompositionStrategy.APPEND,
        name: str | None = None
    ) -> 'GraphModel':
        """Combine this GraphModel with another using an explicit conflict resolution strategy.

        Args:
            other: The right-hand GraphModel to compose with.
            strategy: Conflict resolution strategy (APPEND, OVERRIDE, MERGE, or FAIL).
            name: Optional name for the resulting model. Defaults to ``f"{self.name} + {other.name}"``.

        Returns:
            A new composed GraphModel instance.

        Raises:
            GraphModelError: If strategy is FAIL and overlapping node or edge definitions exist.
        """
        if strategy == CompositionStrategy.FAIL:
            self._check_merge_conflicts(other)

        graph_model = GraphModel(name=name or f"{self.name} + {other.name}")

        if strategy in (CompositionStrategy.APPEND, CompositionStrategy.FAIL):
            self._merge_append(other, graph_model)
        elif strategy == CompositionStrategy.OVERRIDE:
            self._merge_override(other, graph_model)
        elif strategy == CompositionStrategy.MERGE:
            self._merge_combine(other, graph_model)

        return graph_model

    def __add__(self, other: 'GraphModel') -> 'GraphModel':
        return self.merge(other, strategy=CompositionStrategy.APPEND)

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
        if _type is UniverseNode:
            return MappingProxyType({k: v for k, v in self._node_children.items() if k is UniverseNode})
        type_lower = _type.lower() if isinstance(_type, str) else _type
        return MappingProxyType({
            k: v for k, v in self._node_children.items()
            if k == _type or (isinstance(k, str) and k.lower() == type_lower)
        })

    @staticmethod
    def _validate_type(node_type: Any):
        """Validate that the node or edge type is a string identifier or callable.

        Args:
            node_type: The type string, enum value, or callable extractor to validate.

        Raises:
            TypeError: If the type is not a string or a callable.
            ValueError: If the type string is not a valid Python identifier.
        """
        if not callable(node_type):
            if not isinstance(node_type, str):
                raise TypeError(
                    f"Invalid Type: {node_type}. Type must be a string or a callable, not {type(node_type).__name__}."
                )
            if not node_type.isidentifier():
                raise ValueError(f"Invalid Type: {node_type}. Must be a valid Python identifier.")

    def _validate_node_dependency_registration(
            self,
            dependencies: dict[str, str],
            registering_type: str | None = None
    ):
        """Validate that all node dependencies refer to registered node types.

        Args:
            dependencies: Mapping of parameter name to parent node type.
            registering_type: The name of the node type currently being registered.

        Raises:
            GraphModelError: If a dependency target does not match a registered
                node type.
        """
        if any(nm.dynamic_type for nm in itertools.chain.from_iterable(self._node_models.values())):
            return
        node_types_lower = {t.lower() for t in self.node_types}
        if registering_type is not None:
            node_types_lower.add(registering_type.lower())
        for param_name, dep_type in dependencies.items():
            if dep_type is not UniverseNode and dep_type.lower() not in node_types_lower:
                msg = (f"Illegal Arguments: dependency target '{dep_type}' for parameter '{param_name}' "
                       "is not a registered node type. Dependencies must refer to a registered node type.")

                raise GraphModelError(msg)

    def _validate_structural_dependencies(self):
        """Verifies that all registered node dependencies exist within the compiled model.

        Raises:
            GraphModelError: If any node model references a parent/dependency type
                not present in the compiled model's nodes.
        """
        for node_models in self._node_models.values():
            for node_model in node_models:
                if node_model.dependencies:
                    self._validate_node_dependency_registration(
                        node_model.dependencies,
                        registering_type=node_model.type
                    )

    def compile(
            self,
            _type: Extractor | None = None,
            parent_type: str | None = UniverseNode,
            key: Extractor | None = None,
            value: Extractor | None = None,
            label: Extractor | None = None
    ) -> 'GraphModel':
        """Compiles and validates a copy of the graph model.

        Returns:
            A rectified and validated GraphModel clone.

        Raises:
            GraphModelError: If the model configuration has unresolved dependencies.
        """
        compiled_model = GraphModel(name=self.name)
        for k, v in self._node_models.items():
            compiled_model._node_models[k] = list(v)
        for k, v in self._node_children.items():
            compiled_model._node_children[k] = list(v)
        for k, v in self._edge_generators.items():
            compiled_model._edge_generators[k] = list(v)

        compiled_model.rectify(_type=_type, parent_type=parent_type, key=key, value=value, label=label)
        compiled_model._validate_structural_dependencies()
        return compiled_model

    @staticmethod
    def _extract_node_dependencies(f: Items, sig: inspect.Signature) -> dict[str, str]:
        dependencies = {}
        try:
            hints = typing.get_type_hints(f, include_extras=True)
        except Exception:
            hints = {}

        for param_name in sig.parameters:
            hint = hints.get(param_name)
            dep_type = None

            if hint is not None and typing.get_origin(hint) is typing.Annotated:
                for metadata in typing.get_args(hint)[1:]:
                    if isinstance(metadata, ParentId):
                        dep_type = metadata.node_type
                        break

            if (
                dep_type is None
                and param_name.endswith('_id')
                and param_name == param_name.lower()
            ):
                dep_type = param_name[:-3]

            if dep_type is not None:
                dependencies[param_name] = dep_type

        return dependencies

    @staticmethod
    def _prepare_node_kwargs(
        sig: inspect.Signature,
        dependencies: dict[str, str],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        f_kwargs = {}
        for param_name, param in sig.parameters.items():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                f_kwargs.update(kwargs)
            elif param_name in dependencies:
                dep_key = f"{dependencies[param_name]}_id".lower()
                f_kwargs[param_name] = next((v for k, v in kwargs.items() if k.lower() == dep_key), None)
            elif param_name in kwargs:
                f_kwargs[param_name] = kwargs[param_name]
            elif param.default is inspect.Parameter.empty:
                f_kwargs[param_name] = None
        return f_kwargs

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
            The decorated generator function may accept parent node IDs via explicit
            `Annotated[str, ParentId('parent_type')]` type annotations or implicit
            `{parent_type}_id` parameter naming, as well as arbitrary configuration
            parameters passed at build time.

        Returns:
            None
        """

        def register_node(f: Items):
            from enum import Enum
            actual_type = type_.value if isinstance(type_, Enum) else type_
            actual_parent_type = parent_type.value if isinstance(parent_type, Enum) else parent_type

            node_type = actual_type or f.__name__
            self._validate_type(node_type)
            self._validate_type(actual_parent_type)

            model_type = f.__name__ if callable(node_type) else node_type
            sig = inspect.signature(f)
            dependencies = self._extract_node_dependencies(f, sig)

            if inspect.isasyncgenfunction(f) or inspect.iscoroutinefunction(f):
                async def node_generator(**kwargs: Any) -> AsyncIterable[Node]:
                    f_kwargs = self._prepare_node_kwargs(sig, dependencies, kwargs)
                    res = f(**f_kwargs)
                    if inspect.isawaitable(res):
                        res = await res
                    async for item in aelements(res, node_type, key=key, value=value):
                        yield item
            else:
                def node_generator(**kwargs: Any) -> Iterable[Node]:
                    f_kwargs = self._prepare_node_kwargs(sig, dependencies, kwargs)
                    yield from elements(f(**f_kwargs), node_type, key=key, value=value)

            node_model = NodeModel(type=model_type,
                                   parent_type=actual_parent_type,
                                   dependencies=dependencies,
                                   label=label,
                                   uniqueness=unique,
                                   multiplicity=multiplicity,
                                   generator=node_generator,
                                   dynamic_type=callable(node_type))
            self._node_models[node_model.absolute_id].append(node_model)
            self._node_children[actual_parent_type].append(model_type)

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
            from enum import Enum
            actual_type = type_
            if isinstance(actual_type, Enum):
                actual_type = actual_type.value

            edge_type = actual_type or f.__name__
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

            if inspect.isasyncgenfunction(f) or inspect.iscoroutinefunction(f):
                async def edge_generator(**kwargs: Any) -> AsyncIterable[Edge]:
                    res = f(**kwargs)
                    if inspect.isawaitable(res):
                        res = await res
                    async for item in aelements(res, edge_type, **getters):
                        yield item
            else:
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


__all__ = ('GraphModel', 'aelements', 'elements', 'model', 'named_element', 'tuple_element')


