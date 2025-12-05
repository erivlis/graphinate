from abc import ABC, abstractmethod
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from ..converters import edge_label_converter, node_label_converter
from ..enums import GraphType
from ..modeling import GraphModel
from ..typing import GraphRepresentation


class Builder(ABC):
    """Abstract Base Class for Graph Builders.

    This class acts as a blueprint for all concrete builders that generate graph-like
    data structures from a given `GraphModel`.

    Attributes:
        default_node_attributes (Mapping): Default attributes for all nodes.
        default_edge_attributes (Mapping): Default attributes for all edges.
    """

    default_node_attributes: Mapping = MappingProxyType({
        'type': 'node',
        'label': node_label_converter,
        'value': [],
        'lineage': None
    })

    default_edge_attributes: Mapping = MappingProxyType({
        'type': 'edge',
        'label': edge_label_converter,
        'value': [],
        'weight': 1.0
    })

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        """Initialize a Builder instance with a specific graph model and type.

        Args:
            model (GraphModel): The model defining the graph's structure and data.
            graph_type (GraphType): Enum specifying the type of the graph.
        """

        self._cached_build_kwargs: dict[str, Any] = {}
        self.model = model
        self.graph_type = graph_type

    @abstractmethod
    def build(self, **kwargs: Any) -> GraphRepresentation:
        """Build the graph representation.

        Subclasses must override this method to implement specific build logic.

        Args:
            **kwargs: Any additional parameters for the build process.
        """
        self._cached_build_kwargs = MappingProxyType(kwargs)
