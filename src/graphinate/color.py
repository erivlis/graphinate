import functools
from collections.abc import Mapping, Sequence

import matplotlib as mpl
import networkx as nx

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@functools.lru_cache
def node_color_mapping(graph: nx.Graph, cmap: str | mpl.colors.Colormap = 'tab20') -> Mapping:
    """Map node types to RGBA colors based on a colormap.
    Args:
        graph: nx.Graph - The input graph for which node colors need to be mapped.
        cmap: str | mpl.colors.Colormap, optional - The colormap used to map values to RGBA colors.
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

    if HAS_NUMPY:
        color_indices = np.fromiter(
            (type_lookup.get(graph.nodes[node].get('type'), 0) for node in graph.nodes),
            dtype=int,
            count=len(graph),
        )
        if len(color_indices) > 1:
            low, high = color_indices.min(), color_indices.max()
        else:
            low = high = 0
    else:
        color_indices = [type_lookup.get(graph.nodes[node].get('type'), 0) for node in graph.nodes]
        if len(color_indices) > 1:
            low, high = min(color_indices), max(color_indices)
        else:
            low = high = 0

    norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

    # mapper.to_rgba handles both numpy arrays and lists
    colors = mapper.to_rgba(color_indices).tolist()

    color_mapping = dict(zip(graph.nodes, colors))
    return color_mapping


def color_hex(color: str | Sequence[float | int]) -> str | Sequence[float | int]:
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
            msg = 'Input values should either be a float between 0 and 1 or an int between 0 and 255'
            raise ValueError(msg)

        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    else:
        return color


def _can_vectorize_float_colors(colored_nodes: list[tuple[object, object]]) -> bool:
    return bool(colored_nodes) and all(
        isinstance(val, (tuple, list))
        and len(val) >= 3
        and all(isinstance(c, float) and 0 <= c <= 1 for c in val[:3])
        for _, val in colored_nodes
    )


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
    colored_nodes = [(node, data[color]) for node, data in graph.nodes(data=True) if color in data]
    if HAS_NUMPY and _can_vectorize_float_colors(colored_nodes):
        rgb_array = (np.array([val[:3] for _, val in colored_nodes], dtype=float) * 255).astype(int)
        color_values = {
            node: f'#{r:02x}{g:02x}{b:02x}'
            for (node, _), (r, g, b) in zip(colored_nodes, rgb_array.tolist())
        }
    else:
        color_values = {node: color_hex(val) for node, val in colored_nodes}

    nx.set_node_attributes(graph, values=color_values, name=color)
