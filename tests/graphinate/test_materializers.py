from unittest.mock import patch

import graphinate


def test_materialize(map_graph_model, capsys):

    expected_snippet = '"graph": {\n    "name": "Map",'

    with patch('graphinate.materializers.modal_radiobutton_chooser') as modal_radiobutton_chooser:
        modal_radiobutton_chooser.return_value = ('Test', graphinate.materializers.Materializers.D3Graph.value)

        country_count, city_count, graph_model = map_graph_model
        graphinate.materialize(graph_model)
        captured = capsys.readouterr()
        assert expected_snippet in captured.out
        assert captured.err == ""
