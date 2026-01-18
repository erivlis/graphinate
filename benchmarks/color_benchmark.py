import functools
import timeit
from collections.abc import Mapping
from typing import Union

import matplotlib as mpl
import networkx as nx
import numpy as np


# --- Original Implementation ---
@functools.lru_cache
def node_color_mapping_numpy(graph: nx.Graph, cmap: Union[str, mpl.colors.Colormap] = "tab20") -> Mapping:
    if not graph.nodes:
        return {}

    node_type_keys = graph.graph.get('node_types', {}).keys()

    if len(node_type_keys) > 1 and 'node' in node_type_keys:
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


# --- Alternative Implementation (No NumPy) ---
@functools.lru_cache
def node_color_mapping_pure(graph: nx.Graph, cmap: Union[str, mpl.colors.Colormap] = "tab20") -> Mapping:
    if not graph.nodes:
        return {}

    node_type_keys = graph.graph.get('node_types', {}).keys()

    if len(node_type_keys) > 1 and 'node' in node_type_keys:
        final_keys = [k for k in node_type_keys if k != 'node']
    else:
        final_keys = list(node_type_keys)

    type_lookup = {t: i for i, t in enumerate(final_keys)}

    # Generate indices directly
    color_indices = [type_lookup.get(graph.nodes[node].get('type'), 0) for node in graph.nodes]

    if len(color_indices) > 1:
        low, high = min(color_indices), max(color_indices)
    else:
        low = high = 0

    norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

    # mapper.to_rgba accepts a list of values
    colors = mapper.to_rgba(color_indices).tolist()

    color_mapping = dict(zip(graph.nodes, colors))
    return color_mapping


def run_benchmark():
    # Setup a dummy graph
    g = nx.Graph()
    g.graph['node_types'] = {'user': {}, 'post': {}, 'comment': {}}

    # Add a reasonable number of nodes to make the benchmark meaningful
    num_nodes = 10000
    for i in range(num_nodes):
        node_type = 'user' if i % 3 == 0 else ('post' if i % 3 == 1 else 'comment')
        g.add_node(f"n{i}", type=node_type)

    # Warmup
    node_color_mapping_numpy(g)
    node_color_mapping_pure(g)

    # Clear cache for fair comparison if we were calling it multiple times, 
    # but here we just want to measure execution time of the logic.
    # Since lru_cache is on, subsequent calls would be instant.
    # We need to bypass the wrapper or clear cache.
    node_color_mapping_numpy.cache_clear()
    node_color_mapping_pure.cache_clear()

    print(f"Benchmarking with {num_nodes} nodes...")

    t_numpy = timeit.timeit(lambda: node_color_mapping_numpy(g), number=1000)
    print(f"NumPy version: {t_numpy:.4f} seconds (1000 runs)")

    t_pure = timeit.timeit(lambda: node_color_mapping_pure(g), number=1000)
    print(f"Pure Python version: {t_pure:.4f} seconds (1000 runs)")

    diff = (t_pure - t_numpy) / t_numpy * 100
    print(f"Difference: {diff:.2f}%")


if __name__ == "__main__":
    run_benchmark()
