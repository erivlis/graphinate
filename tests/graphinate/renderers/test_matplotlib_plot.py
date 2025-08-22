import networkx as nx


# Plot a simple graph with default parameters (node labels shown, edge labels hidden)
def test_plot_with_default_parameters(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph(name="Test Graph")
    graph.add_node(1, label="Node 1")
    graph.add_edge(1, 2, label="Edge 1-2")

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph)

    # Assert
    mock_draw.assert_called_once_with(graph, True, False)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Test Graph")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a graph with both node and edge labels displayed
def test_plot_with_node_and_edge_labels(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph(name="Test Graph")
    graph.add_node(1, label="Node 1")
    graph.add_edge(1, 2, label="Edge 1-2")

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph, with_node_labels=True, with_edge_labels=True)

    # Assert
    mock_draw.assert_called_once_with(graph, True, True)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Test Graph")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a graph with neither node nor edge labels displayed
def test_plot_without_node_and_edge_labels(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph(name="Test Graph")
    graph.add_node(1, label="Node 1")
    graph.add_edge(1, 2, label="Edge 1-2")

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph, with_node_labels=False, with_edge_labels=False)

    # Assert
    mock_draw.assert_called_once_with(graph, False, False)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Test Graph")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a graph with custom kwargs that are passed to the draw function
def test_plot_with_custom_kwargs(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph(name="Test Graph")
    custom_kwargs = {'node_size': 500, 'alpha': 0.8, 'width': 2.0}

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph, **custom_kwargs)

    # Assert
    mock_draw.assert_called_once_with(graph, True, False, **custom_kwargs)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Test Graph")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a graph with a custom name that appears in the figure title
def test_plot_with_custom_graph_name(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    custom_name = "My Special Graph Visualization"
    graph = nx.Graph(name=custom_name)
    graph.add_node(1)

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph)

    # Assert
    mock_draw.assert_called_once_with(graph, True, False)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with(custom_name)
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot an empty graph (no nodes or edges)
def test_plot_empty_graph(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph(name="Empty Graph")

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph)

    # Assert
    mock_draw.assert_called_once_with(graph, True, False)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Empty Graph")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a graph with no name attribute
def test_plot_graph_without_name(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph()  # No name provided
    graph.add_node(1)

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph)

    # Assert
    mock_draw.assert_called_once_with(graph, True, False)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("")  # Empty string expected
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a very large graph with many nodes and edges
def test_plot_large_graph(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    # Create a large graph
    graph = nx.complete_graph(100)  # 100 nodes, fully connected
    graph.name = "Large Complete Graph"

    # Add labels to nodes and edges
    for node in graph.nodes():
        graph.nodes[node]['label'] = f"Node {node}"
    for edge in graph.edges():
        graph.edges[edge]['label'] = f"Edge {edge[0]}-{edge[1]}"

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph)

    # Assert
    mock_draw.assert_called_once_with(graph, True, False)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Large Complete Graph")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a graph with custom node attributes that aren't 'label'
def test_plot_with_custom_node_attributes(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph(name="Graph with Custom Node Attributes")
    graph.add_node(1, label="Node 1", weight=10, category="A")
    graph.add_node(2, label="Node 2", weight=5, category="B")
    graph.add_edge(1, 2)

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph)

    # Assert
    mock_draw.assert_called_once_with(graph, True, False)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Graph with Custom Node Attributes")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()


# Plot a graph with custom edge attributes that aren't 'label'
def test_plot_with_custom_edge_attributes(mocker):
    # Arrange
    mock_draw = mocker.patch('graphinate.renderers.matplotlib.draw')
    mock_pyplot = mocker.patch('graphinate.renderers.matplotlib.pyplot')
    mock_ax = mocker.MagicMock()
    mock_fig = mocker.MagicMock()
    mock_pyplot.gca.return_value = mock_ax
    mock_pyplot.gcf.return_value = mock_fig

    graph = nx.Graph(name="Graph with Custom Edge Attributes")
    graph.add_node(1, label="Node 1")
    graph.add_node(2, label="Node 2")
    graph.add_edge(1, 2, label="Edge 1-2", weight=5, type="connection")

    # Act
    from graphinate.renderers.matplotlib import plot
    plot(graph, with_edge_labels=True)

    # Assert
    mock_draw.assert_called_once_with(graph, True, True)
    mock_ax.margins.assert_called_once_with(0.10)
    mock_fig.suptitle.assert_called_once_with("Graph with Custom Edge Attributes")
    mock_fig.tight_layout.assert_called_once()
    mock_pyplot.show.assert_called_once()
