import graphinate
import graphinate.builders


def test_networkx_builder(map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model)
    graph = builder.build()

    # assert
    assert graph.order() == country_count + city_count
    assert graph.graph['node_types']['country'] == country_count
    assert graph.graph['node_types']['city'] == city_count

    # from graphinate.plot import show
    # show(graph)


def test_d3_builder(map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # act
    builder = graphinate.builders.D3Builder(graph_model)
    actual_graph = builder.build()

    # assert
    assert actual_graph['directed'] is False
    assert actual_graph['multigraph'] is False
    assert actual_graph['graph']['name'] == 'Map'
    assert actual_graph['graph']['node_types']['city'] == city_count
    assert actual_graph['graph']['node_types']['country'] == country_count
    assert len(actual_graph['nodes']) == city_count + country_count


def test_graphql_builder(map_graph_model, graphql_query):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # act
    builder = graphinate.builders.GraphQLBuilder(graph_model)

    import strawberry
    schema: strawberry.Schema = builder.build()
    execution_result = schema.execute_sync(graphql_query)
    actual_graph = execution_result.data['graph']
    node_types_counts = {c['name']: c['count'] for c in actual_graph['data']['nodeTypes']}

    # assert
    assert actual_graph
    assert actual_graph['data']
    assert actual_graph['data']['name'] == 'Map'
    assert node_types_counts['country'] == country_count
    assert node_types_counts['city'] == city_count
    assert len(actual_graph['nodes']) == country_count + city_count
