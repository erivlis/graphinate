import functools
from collections.abc import Mapping, Sequence
from typing import Union

import matplotlib as mpl
import networkx as nx
import numpy as np


@functools.lru_cache
def node_color_mapping(graph: nx.Graph, cmap: Union[str, mpl.colors.Colormap] = "tab20") -> Mapping:
    """Map node types to RGBA colors based on a colormap.
    Args:
        graph: nx.Graph - The input graph for which node colors need to be mapped.
        cmap: Union[str, mpl.colors.Colormap], optional - The colormap used to map values to RGBA colors.
              Default is "tab20".
    Returns:
        Mapping - A dictionary mapping nodes to their corresponding RGBA colors based on the colormap.

    .. note::
        The graph should have a 'node_types' attribute containing the types of nodes.
        The colormap can be specified as a string or a matplotlib colormap object.
    """
    if not graph.nodes:
        return {}

    node_type_keys = graph.graph.get('node_types', {}).keys()

    if len(node_type_keys) > 1 and 'node' in node_type_keys:
        # Create a new list of keys, preserving order, but excluding 'node'
        final_keys = [k for k in node_type_keys if k != 'node']
    else:
        final_keys = list(node_type_keys)

    type_lookup = {t: i for i, t in enumerate(final_keys)}

    color_values_ndarray = np.fromiter(
        (type_lookup.get(graph.nodes[node].get('type'), 0) for node in graph.nodes),
        dtype=int,
        count=len(graph),
    )
    if len(color_values_ndarray) > 1:
        low, high = color_values_ndarray.min(), color_values_ndarray.max()
    else:
        low = high = 0

    norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    colors = mapper.to_rgba(color_values_ndarray).tolist()

    color_mapping = dict(zip(graph.nodes, colors))
    return color_mapping


def color_hex(color: Union[str, Sequence[Union[float, int]]]) -> Union[str, Sequence[Union[float, int]]]:
    """Get HEX color code

    Args:
        color: input color
    Returns:
         Color HEX code

    .. note::
        If the input is a tuple or list, it should contain either three floats (0-1) or three ints (0-255).
        The function will convert these to a HEX color code.
    """
    if isinstance(color, (tuple, list)):
        rgb = color[:3]

        if all(isinstance(c, float) and 0 <= c <= 1 for c in rgb):
            rgb = tuple(int(c * 255) for c in rgb)
        elif all(isinstance(c, int) and 0 <= c <= 255 for c in rgb):
            rgb = tuple(rgb)
        else:
            msg = "Input values should either be a float between 0 and 1 or an int between 0 and 255"
            raise ValueError(msg)

        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    else:
        return color


def convert_colors_to_hex(graph: nx.Graph, color: str = 'color') -> None:
    """Convert all color labels in the graph to hexadecimal format.

    Args:
        graph (nx.Graph): The input graph with node attributes.
        color (str): The attribute name for the color. Default is 'color'.

    Returns:
        None: The function modifies the graph in place.

    .. note::
       This function assumes that the color attribute is present in the node data.
    """

    color_values = {node: color_hex(data[color]) for node, data in graph.nodes(data=True) if color in data}
    nx.set_node_attributes(graph, values=color_values, name=color)
