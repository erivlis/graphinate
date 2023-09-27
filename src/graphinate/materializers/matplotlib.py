import networkx as nx
from matplotlib import pyplot

from ..color import node_color_mapping


def draw(graph: nx.Graph,
         with_node_labels: bool = True,
         with_edge_labels: bool = False):
    """

    Args:
        graph:
        with_node_labels:
        with_edge_labels:

    Returns:
        None
    """
    pos = nx.planar_layout(graph) if nx.is_planar(graph) else None
    pos = nx.spring_layout(graph, pos=pos) if pos else nx.spring_layout(graph)

    draw_params = {}
    if with_node_labels:
        draw_params.update(
            {
                'with_labels': True,
                'labels': nx.get_node_attributes(graph, 'label'),
                'font_size': 6,
                'font_color': 'blue',
                # 'horizontalalignment':'left',
                # 'verticalalignment':'bottom',
                # 'bbox': {
                #     'boxstyle': 'round',
                #     'fc': (0.02, 0.02, 0.02),
                #     'lw': 0,
                #     'alpha': 0.15,
                #     'path_effects': [patheffects.withStroke(linewidth=1, foreground="red")]
                # }
            }
        )

    node_color = list(node_color_mapping(graph).values())
    nx.draw(graph, pos, node_color=node_color, **draw_params)
    if with_edge_labels:
        nx.draw_networkx_edge_labels(graph,
                                     pos,
                                     edge_labels=nx.get_edge_attributes(graph, 'label'),
                                     font_color='red',
                                     font_size=6)


def plot(graph: nx.Graph,
         with_node_labels: bool = True,
         with_edge_labels: bool = False):
    """

    Args:
        graph:
        with_node_labels:
        with_edge_labels:

    Returns:
        None
    """
    draw(graph, with_node_labels, with_edge_labels)

    ax = pyplot.gca()
    ax.margins(0.10)

    fig = pyplot.gcf()
    fig.suptitle(graph.name)
    fig.tight_layout()

    # pyplot.axis("off")
    pyplot.show()
