import graphinate
import graphinate.builders
import pytest


@pytest.mark.parametrize('execution_number', range(10))
def test_networkx_builder(execution_number, map_graph_model):
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


@pytest.mark.parametrize('execution_number', range(10))
def test_d3_builder(execution_number, map_graph_model):
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


@pytest.mark.parametrize('execution_number', range(10))
def test_graphql_builder(execution_number, map_graph_model, graphql_query):
    # arrange
    country_count, city_count, graph_model = map_graph_model

    # act
    builder = graphinate.builders.GraphQLBuilder(graph_model)

    import strawberry
    schema: strawberry.Schema = builder.build()
    execution_result = schema.execute_sync(graphql_query)
    actual_graph = execution_result.data

    # assert
    assert actual_graph
    assert actual_graph['graph']
    assert actual_graph['nodes']
    assert actual_graph['edges']
    assert actual_graph['graph']['name'] == 'Map'
    node_types_counts = {c['name']: c['value'] for c in actual_graph['graph']['nodeTypeCounts']}
    assert node_types_counts['country'] == country_count
    assert node_types_counts['city'] == city_count
    assert len(actual_graph['nodes']) == country_count + city_count
