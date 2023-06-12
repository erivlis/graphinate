def test_graph_model(map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # assert
    assert len(graph_model._node_models) == 2
    assert len(list(graph_model._node_models[(None, 'Country')].generator())) == country_count  # len(country_ids)
    assert len(list(graph_model._node_models[('Country', 'City')].generator())) == city_count  # len(city_ids)
