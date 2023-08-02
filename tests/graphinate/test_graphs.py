import graphinate
import graphinate.builders


def test_networkx_graph(map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # act
    networkx_graph = graphinate.builders.NetworkxBuilder(graph_model)
    graph = networkx_graph.build()

    # assert
    assert graph.order() == country_count + city_count
    assert graph.graph['node_types']['country'] == country_count
    assert graph.graph['node_types']['city'] == city_count

    # from graphinate.plot import show
    # show(graph)


def test_d3_graph(map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # act
    d3_graph = graphinate.builders.D3Builder(graph_model)
    actual_graph = d3_graph.build()

    # assert
    assert actual_graph['directed'] is False
    assert actual_graph['multigraph'] is False
    assert actual_graph['graph']['name'] == 'Map'
    assert actual_graph['graph']['node_types']['city'] == city_count
    assert actual_graph['graph']['node_types']['country'] == country_count
    assert len(actual_graph['nodes']) == city_count + country_count
