import networkx_mermaid as nxm

import graphinate
from graphinate import GraphType
from graphinate.builders import MermaidBuilder


def test_mermaid_builder__empty_model():
    """Test MermaidBuilder with empty model"""
    # arrange
    name = "Empty Mermaid"
    graph_model = graphinate.model(name=name)

    # act
    builder = MermaidBuilder(graph_model)
    result = builder.build()

    # assert
    assert isinstance(result, str)
    assert name in result


def test_mermaid_builder__with_graph_type():
    """Test MermaidBuilder with specific graph type"""
    # arrange
    name = "DiGraph Mermaid"
    graph_model = graphinate.model(name=name)

    @graph_model.edge()
    def edge():
        for i in range(3):
            yield {'source': i, 'target': i + 1}

    # act
    builder = MermaidBuilder(graph_model, graph_type=GraphType.DiGraph)
    result = builder.build()

    # assert
    assert isinstance(result, str)
    assert name in result


def test_mermaid_builder__with_orientation():
    """Test MermaidBuilder with different orientations"""
    # arrange
    graph_model = graphinate.model(name="Oriented")

    @graph_model.edge()
    def edge():
        yield {'source': 'A', 'target': 'B'}

    # act
    builder = MermaidBuilder(graph_model)
    result_lr = builder.build(orientation=nxm.DiagramOrientation.LEFT_RIGHT)
    result_td = builder.build(orientation=nxm.DiagramOrientation.TOP_DOWN)

    # assert
    assert isinstance(result_lr, str)
    assert isinstance(result_td, str)


def test_mermaid_builder__with_node_shape():
    """Test MermaidBuilder with different node shapes"""
    # arrange
    graph_model = graphinate.model(name="Shaped")

    @graph_model.node()
    def node():
        yield 'A'
        yield 'B'

    # act
    builder = MermaidBuilder(graph_model)
    result_default = builder.build(node_shape=nxm.DiagramNodeShape.DEFAULT)
    result_circle = builder.build(node_shape=nxm.DiagramNodeShape.CIRCLE)

    # assert
    assert isinstance(result_default, str)
    assert isinstance(result_circle, str)


def test_mermaid_builder__with_title():
    """Test MermaidBuilder with custom title"""
    # arrange
    graph_model = graphinate.model(name="Graph")

    @graph_model.node()
    def node():
        yield 'X'

    # act
    builder = MermaidBuilder(graph_model)
    result_with_title = builder.build(title="Custom Title")
    result_empty_title = builder.build(title="")
    result_no_title = builder.build(title=None)

    # assert
    assert isinstance(result_with_title, str)
    assert "Custom Title" in result_with_title
    assert isinstance(result_empty_title, str)
    assert isinstance(result_no_title, str)


def test_mermaid_builder__with_edge_labels():
    """Test MermaidBuilder with edge labels"""
    # arrange
    graph_model = graphinate.model(name="Labeled")

    @graph_model.edge()
    def edge():
        yield {'source': 'A', 'target': 'B', 'label': 'edge1'}

    # act
    builder = MermaidBuilder(graph_model)
    result_without_labels = builder.build(with_edge_labels=False)
    result_with_labels = builder.build(with_edge_labels=True)

    # assert
    assert isinstance(result_without_labels, str)
    assert isinstance(result_with_labels, str)


def test_mermaid_builder__octagonal_graph(octagonal_graph_model):
    """Test MermaidBuilder with the octagonal graph"""
    # act
    builder = MermaidBuilder(octagonal_graph_model)
    result = builder.build()

    # assert
    assert isinstance(result, str)
    assert "Octagonal Graph" in result


def test_mermaid_builder__map_graph_model(map_graph_model):
    """Test MermaidBuilder with a complex map graph model"""
    # arrange
    _country_count, _city_count, graph_model = map_graph_model

    # act
    builder = MermaidBuilder(graph_model)
    result = builder.build()

    # assert
    assert isinstance(result, str)
    assert "Map" in result


def test_mermaid_builder__with_all_parameters():
    """Test MermaidBuilder with all parameters"""
    # arrange
    graph_model = graphinate.model(name="Complete")

    @graph_model.node()
    def node():
        yield 'node1'
        yield 'node2'

    @graph_model.edge()
    def edge():
        yield {'source': 'node1', 'target': 'node2', 'label': 'connects'}

    # act
    builder = MermaidBuilder(graph_model, graph_type=GraphType.DiGraph)
    result = builder.build(
        orientation=nxm.DiagramOrientation.TOP_DOWN,
        node_shape=nxm.DiagramNodeShape.CIRCLE,
        title="Full Test",
        with_edge_labels=True
    )

    # assert
    assert isinstance(result, str)
    assert "Full Test" in result
