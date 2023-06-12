import graphinate


def test_network_factory(map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # act
    networkx_factory = graphinate.NetworkxFactory(graph_model)
    graph = networkx_factory.build()

    # assert
    assert graph.order() == country_count + city_count
    assert graph.graph['types']['country'] == country_count
    assert graph.graph['types']['city'] == city_count

    from graphinate.plot import show
    show(graph)
