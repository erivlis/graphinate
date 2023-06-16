from collections import Counter
from typing import Hashable

import networkx as nx

from ..modeling import UNIVERSE_NODE, GraphModel
from ..typing import NodeTypeAbsoluteId


class NetworkxBuilder:

    def __init__(self, model: GraphModel):
        self.model = model

    def _init_graph(self):
        self._graph = nx.Graph(name=self.model.name, types=Counter())

    def _populate_node_type(self, node_type: Hashable | UNIVERSE_NODE = UNIVERSE_NODE, **kwargs):
        for parent_node_type, child_node_types in self.model.node_children(node_type).items():
            for child_node_type in child_node_types:
                node_type_absolute_id = (parent_node_type, child_node_type)
                self._populate_nodes(node_type_absolute_id, **kwargs)

    def _populate_nodes(self, node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
        node_type = self.model.node_models[node_type_absolute_id]

        unique = node_type.uniqueness
        for node in node_type.generator(**kwargs):
            parent_node_id = (*(kwargs.values()),) if kwargs else UNIVERSE_NODE
            node_lineage = (*parent_node_id, node.key) if parent_node_id is not UNIVERSE_NODE else (node.key,)
            node_id = (node.key,) if unique else node_lineage

            label = node.key
            if node_type.label is not None:
                label = node_type.label(node.value) if callable(node_type.label) else node_type.label

            _type = node_type.type.lower()

            self._graph.add_node(node_id,
                                 label=label,
                                 color='type',
                                 type=_type,
                                 value=node.value,
                                 lineage=list(node_lineage))

            self._graph.graph['types'].update({_type: 1})

            if node_type.parent_type is not UNIVERSE_NODE:
                self._graph.add_edge(node_id, parent_node_id)

            new_kwargs = kwargs.copy()
            new_kwargs[f"{_type}_id"] = node.key
            self._populate_node_type(node_type.type, **new_kwargs)

    def _finalize(self):
        types_counter = self._graph.graph['types']
        self._graph.graph['types'] = dict(types_counter)

    def build(self, **kwargs):
        self._init_graph()
        self._populate_node_type(UNIVERSE_NODE, **kwargs)

        return self._graph


class NetworkxGraph:

    def __init__(self, model: GraphModel):
        self.model = model
        self._builder: NetworkxBuilder = NetworkxBuilder(self.model)

    def build(self, **kwargs) -> nx.Graph:
        graph = self._builder.build(**kwargs)
        return graph


__all__ = ('NetworkxGraph',)
