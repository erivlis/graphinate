from typing import Any

import networkx_mermaid as nxm

from .. import color
from ..enums import GraphType
from ..modeling import GraphModel
from ._networkx import NetworkxBuilder


class MermaidBuilder(NetworkxBuilder):
    """Build a Mermaid Graph"""

    def __init__(self, model: GraphModel, graph_type: GraphType = GraphType.Graph):
        super().__init__(model, graph_type)

    def build(self,
              orientation: nxm.DiagramOrientation = nxm.DiagramOrientation.LEFT_RIGHT,
              node_shape: nxm.DiagramNodeShape = nxm.DiagramNodeShape.DEFAULT,
              title: str | None = None,
              with_edge_labels: bool = False,
              **kwargs: Any) -> nxm.typing.MermaidDiagram:
        """
        Build a Mermaid Graph

        Args:
          orientation : Orientation, optional
            The orientation of the graph, by default Orientation.LEFT_RIGHT.
          node_shape : NodeShape, optional
            The shape of the nodes, by default NodeShape.DEFAULT.
          title: str, optional
            The title of the graph (default: None).
            If None, the graph name will be used if available.
            Supplying and empty string will remove the title.
          with_edge_labels:
            Whether to include edge labels, by default False.
          **kwargs: additional inputs to the node and edge generator functions

        Returns:
            Mermaid Graph
        """
        super().build(**kwargs)
        color.convert_colors_to_hex(self._graph)
        nxm_builder = nxm.DiagramBuilder(orientation=orientation, node_shape=node_shape)
        return nxm_builder.build(self._graph, title=title, with_edge_labels=with_edge_labels)
