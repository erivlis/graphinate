import functools
from unittest.mock import patch

import graphinate
import pytest
from matplotlib import pyplot as plt

MODAL_RADIOBUTTON_CHOOSER = 'graphinate.materializers.modal_radiobutton_chooser'


def test_materialize(map_graph_model, capsys):
    expected_snippet = '"graph": {\n    "name": "Map",'
    *_, graph_model = map_graph_model
    builder, actualizer = graphinate.materializers.Materializers.D3Graph.value
    graphinate.materialize(graph_model, builder=builder, actualizer=actualizer)
    captured = capsys.readouterr()
    assert expected_snippet in captured.out
    assert captured.err == ""


def test_materialize_d3graph(map_graph_model, monkeypatch, capsys):
    monkeypatch.setattr(plt, 'show', lambda: None)

    expected_snippet = '"graph": {\n    "name": "Map",'

    with patch(MODAL_RADIOBUTTON_CHOOSER) as modal_radiobutton_chooser:
        modal_radiobutton_chooser.return_value = ('Test', graphinate.materializers.Materializers.D3Graph.value)

        *_, graph_model = map_graph_model
        graphinate.materialize(graph_model)
        captured = capsys.readouterr()
        assert expected_snippet in captured.out
        assert captured.err == ""


def test_materialize_graphql(map_graph_model, monkeypatch):
    with patch(MODAL_RADIOBUTTON_CHOOSER) as modal_radiobutton_chooser:
        import uvicorn
        monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: None)
        modal_radiobutton_chooser.return_value = ('Test', graphinate.materializers.Materializers.GraphQL.value)

        *_, graph_model = map_graph_model
        graphinate.materialize(graph_model)
        assert True


networkx_materializers = [
    graphinate.materializers.Materializers.NetworkX.value,
    graphinate.materializers.Materializers.NetworkX_with_edge_labels.value,
    (graphinate.builders.NetworkxBuilder,
     functools.partial(graphinate.materializers.matplotlib.plot, with_node_labels=False))

]


@pytest.mark.parametrize('materializer', networkx_materializers)
def test_materialize_networkx(map_graph_model, materializer, monkeypatch):
    with monkeypatch.context():
        monkeypatch.setattr(plt, 'show', lambda: None)
        with patch('graphinate.materializers.modal_radiobutton_chooser') as modal_radiobutton_chooser:
            modal_radiobutton_chooser.return_value = ('Test', materializer)
            *_, graph_model = map_graph_model
            graphinate.materialize(graph_model)
            assert True


def test_materialize_none(map_graph_model, monkeypatch):
    with patch(MODAL_RADIOBUTTON_CHOOSER) as modal_radiobutton_chooser:
        import uvicorn
        monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: None)
        modal_radiobutton_chooser.return_value = ('Test', (None, None))

        *_, graph_model = map_graph_model
        with pytest.raises(ValueError, match="Missing: builder, actualizer"):
            graphinate.materialize(graph_model)
