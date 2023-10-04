import graphinate
import pytest


def test_graph_model(map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # assert
    assert len(graph_model._node_models) == 3
    assert len(list(graph_model._node_models[(graphinate.UNIVERSE_NODE, 'country')].generator())) == country_count  # len(country_ids)
    assert len(list(graph_model._node_models[('country', 'city')].generator())) == city_count  # len(city_ids)


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
