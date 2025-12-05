"""Builder Classes: Abstraction Layer to Generate Graph Data Structures

This module defines builder base classes and implementations that construct graph
data structures from a `GraphModel`. It supports generating various graph formats,
including NetworkX, D3, Mermaid, and GraphQL schema representations.

Attributes:
    - **GraphRepresentation:** Types of representations the builder can produce.
    - **GraphType:** Enumeration for different graph types (directed, undirected, etc.).

Main Classes:
    - `GraphType`    : Enum defining networkx-compatible graph types.
    - `Builder`      : Abstract base class for custom graph builders.
    - `NetworkxBuilder` : A builder class for constructing Graph representations using NetworkX.
    - `D3Builder`    : Builder class transforming graphs into D3-compatible structures.
    - `MermaidBuilder`: Supports MermaidJS diagram generation.
    - `GraphQLBuilder`: Constructs GraphQL schema representations of graphs.
"""

__all__ = ['Builder', 'D3Builder', 'GraphQLBuilder', 'MermaidBuilder', 'NetworkxBuilder', 'build']

from collections.abc import Mapping
from typing import Any

from ..enums import GraphType
from ..modeling import GraphModel
from ._builder import Builder
from ._d3 import D3Builder
from ._graphql import GraphQLBuilder
from ._mermaid import MermaidBuilder
from ._networkx import NetworkxBuilder


def build(builder_cls: type[Builder],
          graph_model: GraphModel,
          graph_type: GraphType = GraphType.Graph,
          default_node_attributes: Mapping | None = None,
          **kwargs: Any) -> Any:
    """
    Build a graph from a graph model

    Args:
        builder_cls: builder class type
        graph_model: a GraphModel instance
        graph_type: type of the generated graph
        default_node_attributes: default node attributes
        **kwargs: node id values

    Returns:
         Graph data structure
    """

    builder = builder_cls(graph_model, graph_type)
    materialized_graph = builder.build(default_node_attributes=default_node_attributes, **kwargs)
    return materialized_graph
