from graphinate.builders import Builder, build
from graphinate.enums import GraphType
from graphinate.modeling import GraphModel


class MockBuilder(Builder):
    def build(self, **kwargs):
        return {"built": True, "kwargs": kwargs}


def test_build_returns_graph_data_structure():
    # Arrange
    graph_model = GraphModel(name="TestModel")
    graph_type = GraphType.Graph
    default_node_attributes = {"attribute": "value"}
    builder_cls = MockBuilder

    # Act
    result = build(
        builder_cls=builder_cls,
        graph_model=graph_model,
        graph_type=graph_type,
        default_node_attributes=default_node_attributes,
        custom_arg="custom_value"
    )

    # Assert
    assert result == {
        "built": True,
        "kwargs": {
            "default_node_attributes": {"attribute": "value"},
            "custom_arg": "custom_value",
        },
    }


def test_build_invokes_builder_with_correct_arguments(mocker):
    # Arrange
    graph_model = GraphModel(name="TestModel")
    builder_cls = MockBuilder
    graph_type = GraphType.DiGraph

    mock_init = mocker.patch.object(MockBuilder, '__init__', return_value=None)
    mock_build = mocker.patch.object(MockBuilder, 'build', return_value={"mocked": True})

    # Act
    build(builder_cls=builder_cls, graph_model=graph_model, graph_type=graph_type)

    # Assert
    mock_init.assert_called_once_with(graph_model, graph_type)
    mock_build.assert_called_once_with(default_node_attributes=None)
