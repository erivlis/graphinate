import networkx as nx
import numpy as np
import pytest

from graphinate.color import color_hex, node_color_mapping

colors = [
    ([0, 0, 0], '#000000'),
    ([0.5, 0.5, 0.5], '#7f7f7f'),
    ([1, 1, 1], '#010101'),  # This is a list of ints, not floats
    ([2, 2, 2], '#020202'),
    ([50, 50, 50], '#323232'),
    ([100, 100, 100], '#646464'),
    ([128, 128, 128], '#808080'),
    ([255, 255, 255], '#ffffff'),
    ('Not a Sequence', 'Not a Sequence'),
]


@pytest.mark.parametrize(('color', 'expected_color_hex'), colors)
def test_color_hex(color, expected_color_hex):
    # act
    actual_color_hex = color_hex(color)

    # assert
    assert actual_color_hex == expected_color_hex


def test_color_hex_error():
    with pytest.raises(
            ValueError,
            match='Input values should either be a float between 0 and 1 or an int between 0 and 255',
    ):
        _ = color_hex(['a', 'b', 'c'])


def test_node_color_mapping_empty_graph():
    # arrange
    g = nx.Graph()

    # act
    color_map = node_color_mapping(g)

    # assert
    assert color_map == {}


def test_node_color_mapping_multiple_types():
    # arrange
    g = nx.Graph()
    g.graph['node_types'] = {'user': {}, 'post': {}}
    g.add_node('u1', type='user')
    g.add_node('u2', type='user')
    g.add_node('p1', type='post')

    # act
    color_map = node_color_mapping(g)

    # assert
    assert len(color_map) == 3
    assert np.array_equal(color_map['u1'], color_map['u2'])  # Same type, same color
    assert not np.array_equal(color_map['u1'], color_map['p1'])  # Different types, different colors


def test_node_color_mapping_filters_generic_node_type():
    # arrange
    g = nx.Graph()
    # The 'node' type should be ignored in color calculations if other types exist
    g.graph['node_types'] = {'user': {}, 'post': {}, 'node': {}}
    g.add_node('u1', type='user')
    g.add_node('p1', type='post')
    g.add_node('n1', type='node')  # This should get a default color

    # act
    color_map = node_color_mapping(g)

    # assert
    # 'user' and 'post' should have distinct colors
    assert not np.array_equal(color_map['u1'], color_map['p1'])
    # 'node' type should map to the first color in the sequence (same as 'user' in this case)
    # because 'user' will be at index 0 and 'post' at index 1 after filtering.
    assert np.array_equal(color_map['n1'], color_map['u1'])


def test_node_color_mapping_with_only_generic_node_type():
    # arrange
    g = nx.Graph()
    # If 'node' is the only type, it should NOT be filtered
    g.graph['node_types'] = {'node': {}}
    g.add_node('n1', type='node')
    g.add_node('n2', type='node')

    # act
    color_map = node_color_mapping(g)

    # assert
    assert len(color_map) == 2
    assert np.array_equal(color_map['n1'], color_map['n2'])  # All nodes get the same color


def test_node_color_mapping_no_node_types_in_graph():
    # arrange
    g = nx.Graph()
    g.add_node('u1', type='user')
    g.add_node('p1', type='post')

    # act
    color_map = node_color_mapping(g)

    # assert
    # Without `node_types`, all nodes get the default color (index 0)
    assert len(color_map) == 2
    assert np.array_equal(color_map['u1'], color_map['p1'])


def test_node_color_mapping_equivalence():
    # arrange
    g = nx.Graph()
    g.graph['node_types'] = {'user': {}, 'post': {}, 'comment': {}}
    g.add_node('u1', type='user')
    g.add_node('u2', type='user')
    g.add_node('p1', type='post')
    g.add_node('c1', type='comment')
    g.add_node('n1')  # node with no type

    # act
    color_map = node_color_mapping(g)

    # assert
    assert set(color_map.keys()) == {'u2', 'u1', 'p1', 'n1', 'c1'}
    assert len({tuple(v) for v in color_map.values()}) == 3


def test_color_hex_compatibility_with_node_color_mapping_outputs():
    # arrange
    g = nx.Graph()
    g.graph['node_types'] = {'user': {}, 'post': {}}
    g.add_node('u1', type='user')
    g.add_node('p1', type='post')

    # act
    color_map = node_color_mapping(g)

    # assert
    # Check that color_hex works for the new function's output
    for color in color_map.values():
        hex_color = color_hex(color)
        assert isinstance(hex_color, str)
        assert hex_color.startswith('#')
        assert len(hex_color) == 7
