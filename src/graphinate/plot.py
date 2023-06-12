import networkx as nx

import matplotlib as mpl
from matplotlib import pyplot as plt


def color_map(graph: nx.Graph, cmap: str | mpl.colors.Colormap = "coolwarm"):
    """
    graph: graph_id
    cmap : str or `~matplotlib.colors.Colormap` - The colormap used to map values to RGBA colors.
    :return: Nodes RGBA Color list
    """
    type_lookup = {t: i for i, t in enumerate(graph.graph['types'].keys())}
    color_lookup = [type_lookup[data['type']] for node, data in graph.nodes.data()]
    low, *_, high = sorted(color_lookup)
    norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    node_color = [mapper.to_rgba(i) for i in color_lookup]
    return node_color


def draw(graph: nx.Graph):
    node_color_map = color_map(graph)
    nx.draw(graph, with_labels=True, node_color=node_color_map)


def show(graph: nx.Graph):
    draw(graph)
    plt.show()
