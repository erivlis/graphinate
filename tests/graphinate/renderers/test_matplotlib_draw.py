import networkx as nx

from graphinate.renderers.matplotlib import draw


# Drawing a graph with default parameters (node labels on, edge labels off)
def test_draw_with_default_parameters(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_nx_draw_edge_labels = mocker.patch('networkx.draw_networkx_edge_labels')
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='mock_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=False)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0, label='Node0')
    graph.add_node(1, label='Node1')
    graph.add_edge(0, 1)

    # Act
    draw(graph)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once_with(graph)
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_nx_draw.assert_called_once()
    mock_nx_draw_edge_labels.assert_not_called()


# Drawing a graph with node labels turned off
def test_draw_with_node_labels_off(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='mock_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=False)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0, label='Node0')
    graph.add_node(1, label='Node1')
    graph.add_edge(0, 1)

    # Act
    draw(graph, with_node_labels=False)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once_with(graph)
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_nx_draw.assert_called_once()
    # Check that 'with_labels' is not in the draw parameters
    _args, kwargs = mock_nx_draw.call_args
    assert 'with_labels' not in kwargs


# Drawing a graph with edge labels turned on
def test_draw_with_edge_labels_on(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_nx_draw_edge_labels = mocker.patch('networkx.draw_networkx_edge_labels')
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='mock_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=False)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0, label='Node0')
    graph.add_node(1, label='Node1')
    graph.add_edge(0, 1, label='Edge0-1')

    # Act
    draw(graph, with_edge_labels=True)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once_with(graph)
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_nx_draw.assert_called_once()
    mock_nx_draw_edge_labels.assert_called_once()


# Drawing a graph with both node and edge labels turned on
def test_draw_with_both_labels_on(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_nx_draw_edge_labels = mocker.patch('networkx.draw_networkx_edge_labels')
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='mock_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=False)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0, label='Node0')
    graph.add_node(1, label='Node1')
    graph.add_edge(0, 1, label='Edge0-1')

    # Act
    draw(graph, with_node_labels=True, with_edge_labels=True)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once_with(graph)
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_nx_draw.assert_called_once()
    mock_nx_draw_edge_labels.assert_called_once()

    # Check that node labels are enabled
    _args, kwargs = mock_nx_draw.call_args
    assert kwargs.get('with_labels') is True


# Drawing a planar graph uses planar_layout first
def test_draw_planar_graph(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_planar_layout = mocker.patch('networkx.planar_layout', return_value='planar_pos')
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='spring_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=True)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0)
    graph.add_node(1)
    graph.add_edge(0, 1)

    # Act
    draw(graph)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_planar_layout.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once_with(graph, pos='planar_pos')
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_nx_draw.assert_called_once()


# Drawing a non-planar graph uses spring_layout directly
def test_draw_non_planar_graph(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_planar_layout = mocker.patch('networkx.planar_layout')
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='spring_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=False)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0)
    graph.add_node(1)
    graph.add_edge(0, 1)

    # Act
    draw(graph)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_planar_layout.assert_not_called()
    mock_spring_layout.assert_called_once_with(graph)
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_nx_draw.assert_called_once()


# Drawing an empty graph
def test_draw_empty_graph(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value={})
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=True)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={})

    graph = nx.Graph()

    # Act
    draw(graph)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once()
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_nx_draw.assert_called_once()

    # Check that node_color is an empty list for empty graph
    _args, kwargs = mock_nx_draw.call_args
    assert kwargs.get('node_color') == []


# Drawing a graph with no node attributes for labels when with_node_labels=True
def test_draw_no_node_labels_attribute(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_get_node_attributes = mocker.patch('networkx.get_node_attributes', return_value={})
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='mock_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=False)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0)  # No label attribute
    graph.add_node(1)  # No label attribute
    graph.add_edge(0, 1)

    # Act
    draw(graph, with_node_labels=True)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once_with(graph)
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_get_node_attributes.assert_called_once_with(graph, 'label')
    mock_nx_draw.assert_called_once()

    # Check that labels parameter is empty dict
    _args, kwargs = mock_nx_draw.call_args
    assert kwargs.get('labels') == {}


# Drawing a graph with no edge attributes for labels when with_edge_labels=True
def test_draw_no_edge_labels_attribute(mocker):
    # Arrange
    mock_nx_draw = mocker.patch('networkx.draw')
    mock_nx_draw_edge_labels = mocker.patch('networkx.draw_networkx_edge_labels')
    mock_get_edge_attributes = mocker.patch('networkx.get_edge_attributes', return_value={})
    mock_spring_layout = mocker.patch('networkx.spring_layout', return_value='mock_pos')
    mock_is_planar = mocker.patch('networkx.is_planar', return_value=False)
    mock_node_color_mapping = mocker.patch('graphinate.renderers.matplotlib.node_color_mapping',
                                           return_value={0: 'red', 1: 'blue'})

    graph = nx.Graph()
    graph.add_node(0)
    graph.add_node(1)
    graph.add_edge(0, 1)  # No label attribute

    # Act
    draw(graph, with_edge_labels=True)

    # Assert
    mock_is_planar.assert_called_once_with(graph)
    mock_spring_layout.assert_called_once_with(graph)
    mock_node_color_mapping.assert_called_once_with(graph)
    mock_get_edge_attributes.assert_called_once_with(graph, 'label')
    mock_nx_draw.assert_called_once()
    mock_nx_draw_edge_labels.assert_called_once()

    # Check that the edge_labels parameter is an empty dict
    _args, kwargs = mock_nx_draw_edge_labels.call_args
    assert kwargs.get('edge_labels') == {}
