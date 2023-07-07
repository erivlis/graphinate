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

    @staticmethod
    def _parent_node_id(node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
        if node_type_absolute_id[0] is UNIVERSE_NODE:
            return UNIVERSE_NODE
        else:
            ids = []
            for k, v in kwargs.items():
                if k[:-3] == node_type_absolute_id[1]:
                    break
                ids.append(v)
            return tuple(ids)

        # return (*(kwargs.values()),) if kwargs else UNIVERSE_NODE

    def _populate_nodes(self, node_type_absolute_id: NodeTypeAbsoluteId, **kwargs):
        node_model = self.model.node_models[node_type_absolute_id]
        unique = node_model.uniqueness
        for node in node_model.generator(**kwargs):
            parent_node_id = self._parent_node_id(node_type_absolute_id, **kwargs)
            node_lineage = (*parent_node_id, node.key) if parent_node_id is not UNIVERSE_NODE else (node.key,)
            node_id = (node.key,) if unique else node_lineage

            label = node.key
            if node_model.label is not None:
                label = node_model.label(node.value) if callable(node_model.label) else node_model.label

            model_type = node_model.type.lower()

            self._graph.add_node(node_id,
                                 label=label,
                                 color='type',
                                 type=model_type,
                                 value=node.value,
                                 lineage=list(node_lineage))

            self._graph.graph['types'].update({model_type: 1})

            if node_model.parent_type is not UNIVERSE_NODE:
                self._graph.add_edge(node_id, parent_node_id)

            new_kwargs = kwargs.copy()
            new_kwargs[f"{model_type}_id"] = node.key
            self._populate_node_type(node_model.type, **new_kwargs)

    def _finalize(self):
        types_counter = self._graph.graph['types']
        self._graph.graph['types'] = dict(types_counter)

    def build(self, **kwargs):
        self._init_graph()
        self._populate_node_type(**kwargs)
        return self._graph


class NetworkxGraph:

    def __init__(self, model: GraphModel):
        self.model = model
        self._builder: NetworkxBuilder = NetworkxBuilder(self.model)

    def build(self, **kwargs) -> nx.Graph:
        graph = self._builder.build(**kwargs)
        return graph


__all__ = ('NetworkxGraph',)
