import networkx as nx
from matplotlib import pyplot as plt

from ..color import node_color_mapping


def nodes_labels(graph: nx.Graph):
    # return {node: data.get('label', node) or node for node, data in graph.nodes.data()}
    return nx.get_node_attributes(graph, 'label')


def edges_labels(graph: nx.Graph):
    return nx.get_edge_attributes(graph, 'label')


def draw(graph: nx.Graph, with_labels=True):
    pos = nx.planar_layout(graph) if nx.is_planar(graph) else None
    if pos:
        pos = nx.spring_layout(graph, pos=pos)
    else:
        pos = nx.spring_layout(graph)

    draw_params = {}
    if with_labels:
        draw_params.update(
            {
                'with_labels': True,
                'labels': nodes_labels(graph),
                'font_size': 6,
                'font_color': 'blue',
                # 'horizontalalignment':'left',
                # 'verticalalignment':'bottom',
                # 'bbox': {'boxstyle': 'round', 'fc': (0.02, 0.02, 0.02), 'lw': 0, 'alpha': 0.15, 'path_effects': [patheffects.withStroke(linewidth=1, foreground="red")]}
            }
        )

    node_color = list(node_color_mapping(graph).values())
    nx.draw(graph, pos, node_color=node_color, **draw_params)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edges_labels(graph), font_color='red', font_size=6)


def show(graph: nx.Graph):
    draw(graph)
    plt.show()
