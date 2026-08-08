"""Benchmarks for the color helpers used when finalizing every graph."""

import pytest

from graphinate.color import color_hex, convert_colors_to_hex, node_color_mapping

# node_color_mapping is lru_cached on the graph instance, bypass the cache so that
# the mapping logic is actually measured on every iteration.
_node_color_mapping = node_color_mapping.__wrapped__


def test_node_color_mapping(benchmark, mesh_graph):
    mapping = benchmark(_node_color_mapping, mesh_graph)

    assert len(mapping) == mesh_graph.number_of_nodes()


def test_convert_colors_to_hex(benchmark, mesh_graph):
    benchmark(convert_colors_to_hex, mesh_graph)

    assert all(isinstance(data['color'], str) for _, data in mesh_graph.nodes(data=True))


@pytest.mark.benchmark
def test_color_hex():
    for i in range(1000):
        value = (i % 256) / 255
        color_hex((value, 1 - value, value / 2, 1.0))
