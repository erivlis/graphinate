import functools

import pytest
from matplotlib import pyplot as plt

import examples.math.materializers
import graphinate


def test_materialize(map_graph_model, capsys):
    # Arrange
    expected_snippet = '"graph": {\n    "name": "Map",'
    *_, graph_model = map_graph_model
    builder, handler = examples.math.materializers.Materializers.D3Graph.value

    # Act
    examples.math.materializers.materialize(graph_model, builder=builder, builder_output_handler=handler)
    captured = capsys.readouterr()

    # Assert
    assert expected_snippet in captured.out
    assert captured.err == ""


def test_materialize_d3graph(map_graph_model, monkeypatch, capsys):
    # Arrange
    monkeypatch.setattr(plt, 'show', lambda: None)
    *_, graph_model = map_graph_model
    builder, handler = examples.math.materializers.Materializers.D3Graph.value

    expected_snippet = '"graph": {\n    "name": "Map",'

    # Act
    examples.math.materializers.materialize(graph_model, builder=builder, builder_output_handler=handler)
    captured = capsys.readouterr()

    # Assert
    assert expected_snippet in captured.out
    assert captured.err == ""


def valid_materialization(*args, **kwargs) -> bool:
    examples.math.materializers.materialize(*args, **kwargs)
    return True


def test_materialize_graphql(map_graph_model, monkeypatch):
    with monkeypatch.context():
        # Arrange
        import uvicorn
        monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: None)
        *_, graph_model = map_graph_model
        builder, handler = examples.math.materializers.Materializers.GraphQL.value

        # Act & Assert
        assert valid_materialization(graph_model, builder=builder, builder_output_handler=handler)


networkx_materializers = [
    examples.math.materializers.Materializers.NetworkX.value,
    examples.math.materializers.Materializers.NetworkX_with_edge_labels.value,
    (graphinate.builders.NetworkxBuilder,
     functools.partial(graphinate.materializers.matplotlib.plot, with_node_labels=False))
]


@pytest.mark.parametrize('materializer', networkx_materializers)
def test_materialize_networkx(map_graph_model, materializer, monkeypatch):
    with monkeypatch.context():
        monkeypatch.setattr(plt, 'show', lambda: None)

        # Arrange
        *_, graph_model = map_graph_model
        builder, handler = materializer

        # Act & Assert
        assert valid_materialization(graph_model, builder=builder, builder_output_handler=handler)


def test_materialize_none(map_graph_model, monkeypatch):
    # Arrange
    import uvicorn
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: None)
    *_, graph_model = map_graph_model

    # Act & Assert
    with pytest.raises(ValueError, match="Missing: builder, builder_output_handler"):
        examples.math.materializers.materialize(graph_model, builder=None, builder_output_handler=None)
