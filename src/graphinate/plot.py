import matplotlib as mpl
import networkx as nx
from matplotlib import pyplot as plt, patheffects


def color_map(graph: nx.Graph, cmap: str | mpl.colors.Colormap = "coolwarm"):
    """
    graph: graph_id
    cmap : str or `~matplotlib.colors.Colormap` - The colormap used to map values to RGBA colors.
    :return: Nodes RGBA Color list
    """
    type_lookup = {t: i for i, t in enumerate(graph.graph['types'].keys())}
    color_lookup = [type_lookup.get(data.get('type'), 0) for node, data in graph.nodes.data()]
    if len(color_lookup) > 1:
        low, *_, high = sorted(color_lookup)
    else:
        low = high = 0
    norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    node_color = [mapper.to_rgba(i) for i in color_lookup]
    return node_color


def labels(graph: nx.Graph):
    return {node: data.get('label', node) or node for node, data in graph.nodes.data()}


def draw(graph: nx.Graph, with_labels=True):
    node_color_map = color_map(graph)
    pos = nx.planar_layout(graph) if nx.is_planar(graph) else None
    pos = nx.spring_layout(graph, pos=pos)

    draw_params = {}
    if with_labels:
        draw_params.update(
            {
                'with_labels': True,
                'labels': labels(graph),
                'font_size': 6,
                'font_color': 'white',
                # 'horizontalalignment':'left',
                # 'verticalalignment':'bottom',
                'bbox': {'boxstyle': 'round', 'fc': (0.02, 0.02, 0.02), 'lw': 0, 'alpha': 0.35,
                         'path_effects': [patheffects.withStroke(linewidth=1, foreground="red")]}
            }
        )

    nx.draw(graph, pos, node_color=node_color_map, **draw_params)


def show(graph: nx.Graph):
    draw(graph)
    plt.show()
