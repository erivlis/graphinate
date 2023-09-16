import functools
from collections.abc import Iterable, Mapping
from typing import Union

import matplotlib as mpl
import networkx as nx


@functools.lru_cache
def node_color_mapping(graph: nx.Graph, cmap: Union[str, mpl.colors.Colormap] = "tab20") -> Mapping:
    """
    Parameters:
        graph: graph_id
        cmap : str or `~matplotlib.colors.Colormap` - The colormap used to map values to RGBA colors.
    Returns:
        Nodes RGBA Color list.
    """
    type_lookup = {t: i for i, t in enumerate(graph.graph['node_types'].keys())}
    color_lookup = {node: type_lookup.get(data.get('type'), 0) for node, data in graph.nodes.data()}
    if len(color_lookup) > 1:
        low, *_, high = sorted(color_lookup.values())
    else:
        low = high = 0
    norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    node_colors = {n: mapper.to_rgba(i) for n, i in color_lookup.items()}
    return node_colors


def color_hex(color: Iterable[int]) -> str:
    """Get HEX color code

    Parameters:
        color: input color
    Return:
         Color HEX code
    """
    if isinstance(color, (tuple, list, Iterable)):
        rgb = color[:3]

        if all(0 <= c <= 1 for c in rgb):
            rgb = tuple(int(c * 255) for c in rgb)
        elif all(0 <= c <= 100 for c in rgb):
            rgb = tuple(int(c * 2.55) for c in rgb)
        elif all(0 <= c <= 255 for c in rgb):
            rgb = tuple(int(c) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    return color
