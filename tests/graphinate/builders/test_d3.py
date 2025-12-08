import pytest

import graphinate.builders


@pytest.mark.parametrize('execution_number', range(5))
def test_d3_builder__map_graph_model(execution_number, map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model
    person_count = city_count

    # act
    builder = graphinate.builders.D3Builder(graph_model)
    actual_graph = builder.build()

    # assert
    assert actual_graph['directed'] is False
    assert actual_graph['multigraph'] is False
    assert actual_graph['graph']['name'] == 'Map'
    assert actual_graph['graph']['node_types']['country'] == country_count
    assert actual_graph['graph']['node_types']['city'] == city_count
    assert len(actual_graph['nodes']) == country_count + city_count + person_count


def test_d3_builder__map_graph_model__both_specific_ids(map_graph_model):
    # arrange
    _, _, graph_model = map_graph_model

    # act
    builder = graphinate.builders.D3Builder(graph_model)
    actual_graph = builder.build(country_id="1", city_id="1")

    # assert
    assert actual_graph['directed'] is False
    assert actual_graph['multigraph'] is False
    assert actual_graph['graph']['name'] == 'Map'
    assert actual_graph['graph']['node_types'].get('city', 0) in (0, 1)
    assert actual_graph['graph']['node_types']['country'] == 1
    assert len(actual_graph['nodes']) in (1, 3)


def test_d3_builder_json_format(map_graph_model):
    # arrange
    _, _, graph_model = map_graph_model
    builder = graphinate.builders.D3Builder(graph_model)

    # act
    actual_graph = builder.build(values_format='json')

    # assert

    assert actual_graph

    #assert dates where converted to iso

    # for node in actual_graph['nodes']:
    #     if node.get('value'):
    #         for v in node['value']:
    #             assert isinstance(v, str)
    #             json.loads(v)  # Check if it's a valid JSON string


def test_d3_builder_invalid_format(map_graph_model):
    # arrange
    _, _, graph_model = map_graph_model
    builder = graphinate.builders.D3Builder(graph_model)

    # act & assert
    with pytest.raises(ValueError, match="Invalid values format: invalid_format"):
        builder.build(values_format='invalid_format')
