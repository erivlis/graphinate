import functools
from collections.abc import Mapping, Sequence
from typing import Union

import matplotlib as mpl
import networkx as nx


@functools.lru_cache
def node_color_mapping(graph: nx.Graph, cmap: Union[str, mpl.colors.Colormap] = "tab20") -> Mapping:
    """
    Parameters:
        graph: nx.Graph - The input graph for which node colors need to be mapped.
        cmap: Union[str, mpl.colors.Colormap], optional - The colormap used to map values to RGBA colors.
              Default is "tab20".
    Returns:
        Mapping - A dictionary mapping nodes to their corresponding RGBA colors based on the colormap.
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


def color_hex(color: Union[str, Sequence[Union[float, int]]]) -> Union[str, Sequence[Union[float, int]]]:
    """Get HEX color code

    Parameters:
        color: input color
    Returns:
         Color HEX code
    """
    if isinstance(color, (tuple, list)):  # noqa: UP038
        rgb = color[:3]

        if all(isinstance(c, float) and 0 <= c <= 1 for c in rgb):
            rgb = tuple(int(c * 255) for c in rgb)
        elif all(isinstance(c, int) and 0 <= c <= 255 for c in rgb):
            rgb = tuple(rgb)
        else:
            msg = "Input values should either be a float between 0 and 1 or an int between 0 and 255"
            raise ValueError(msg)

        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    else:
        return color

def convert_colors_to_hex(graph: nx.Graph):
    """Convert all color labels in the graph to hexadecimal format."""
    color_values = {node: color_hex(data['color']) for node, data in graph.nodes(data=True) if 'color' in data}
    nx.set_node_attributes(graph, values=color_values, name='color')
