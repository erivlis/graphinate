import pytest

import graphinate
import graphinate.typing


def test_graph_model(map_graph_model):
    # arrange
    expected_country_count, expected_city_count, graph_model = map_graph_model
    country_type_id = (graphinate.typing.UniverseNode, 'country')
    city_type_id = ('country', 'city')

    # act
    actual_model_count = len(graph_model._node_models)
    actual_country_count = len(list(graph_model._node_models[country_type_id][0].generator()))
    actual_city_count = len(list(graph_model._node_models[city_type_id][0].generator()))

    # assert
    assert actual_model_count == 3
    assert actual_country_count == expected_country_count  # len(country_ids)
    assert actual_city_count == expected_city_count  # len(city_ids)


def test_graph_model__add__():
    first_model = graphinate.model(name='First Model')
    second_model = graphinate.model(name='Second Model')

    actual_model = first_model + second_model

    assert actual_model.name == 'First Model + Second Model'


def test_graph_model_validate_node_parameters():
    graph_model = graphinate.model(name='Graph with invalid node supplier')

    with pytest.raises(graphinate.modeling.GraphModelError):
        @graph_model.node()
        def invalid_node_supplier(wrong_parameter=None):
            yield 1
