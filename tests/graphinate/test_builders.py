import graphinate.builders
import networkx as nx
import pytest


@pytest.mark.parametrize('case', [0, None, "", False])
def test_label_converter__value__falsy(case):
    actual = graphinate.builders.label_converter(case, delimiter=graphinate.builders.DEFAULT_NODE_DELIMITER)
    assert actual == case


def test_encoding():
    expected_edge = (("parent_a", "child_a"), ("parent_b", "child_b"))

    edge_id = graphinate.builders.encode_edge_id(expected_edge)
    actual_edge = graphinate.builders.decode_edge_id(edge_id)

    assert actual_edge == expected_edge


def test_networkx_builder__empty_model():
    # arrange
    name = ""
    graph_model = graphinate.model(name=name)

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model)
    graph = builder.build()

    # assert
    assert isinstance(graph, nx.Graph)
    assert graph.graph['name'] == name


@pytest.mark.parametrize('graph_type', list(graphinate.GraphType))
def test_networkx_builder__graph_type(graph_type):
    # arrange
    name = str(graph_type)
    graph_model = graphinate.model(name=name)

    @graph_model.edge()
    def edge():
        for i in range(5):
            yield {'source': i, 'target': i + 1}
            if graph_type in (graphinate.GraphType.DiGraph, graphinate.GraphType.MultiDiGraph):
                yield {'source': i + 1, 'target': i}
            if graph_type in (graphinate.GraphType.MultiGraph, graphinate.GraphType.MultiDiGraph):
                yield {'source': i, 'target': i + 1}

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model, graph_type=graph_type)
    graph = builder.build()

    # assert
    assert isinstance(graph, nx.Graph)
    assert graph.graph['name'] == name


def test_networkx_builder_repeating_edges():
    # arrange
    name = 'Repeating Nodes'
    graph_model = graphinate.GraphModel(name=name)

    @graph_model.edge()
    def edge():
        for i in range(5):
            e = {'source': i, 'target': i + 1}
            yield e
            yield e

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model)
    graph = builder.build()

    # assert
    assert isinstance(graph, nx.Graph)
    assert graph.graph['name'] == name


def test_networkx_builder_simple_tuple():
    # arrange
    name = 'Simple Tuple'
    graph_model = graphinate.GraphModel(name=name)

    @graph_model.edge()
    def edge():
        for i in range(5):
            yield {'source': (i,), 'target': (i + 1,)}

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model)
    graph = builder.build()

    # assert
    assert isinstance(graph, nx.Graph)
    assert graph.graph['name'] == name


def test_networkx_builder__defaults():
    # arrange
    name = 'Simple Tuple'
    graph_model = graphinate.GraphModel(name=name)

    @graph_model.edge()
    def edge():
        for i in range(5):
            yield {'source': (i,), 'target': (i + 1,)}

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model)
    graph = builder.build()

    # assert
    assert isinstance(graph, nx.Graph)
    assert graph.graph['name'] == name


@pytest.mark.parametrize('execution_number', range(5))
def test_networkx_builder__map_graph_model(execution_number, map_graph_model):
    # arrange
    country_count, city_count, graph_model = map_graph_model
    person_count = city_count

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model)
    graph = builder.build()

    # assert
    assert graph.order() == country_count + city_count + person_count
    assert graph.graph['node_types']['country'] == country_count
    assert graph.graph['node_types']['city'] == city_count


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
    assert actual_graph['graph']['node_types']['city'] == city_count
    assert actual_graph['graph']['node_types']['country'] == country_count
    assert len(actual_graph['nodes']) == country_count + city_count + person_count


@pytest.mark.parametrize('execution_number', range(5))
def test_graphql_builder__map_graph_model(execution_number, map_graph_model, graphql_query):
    # arrange
    country_count, city_count, graph_model = map_graph_model
    person_count = city_count

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
    assert len(actual_graph['nodes']) == country_count + city_count + person_count


def test_graphql_builder_measures():
    # arrange

    graph_model = graphinate.model(name="Octagonal Graph")
    number_of_sides = 8
    graphql_query = """{
      empty: measure(measure: is_empty) {
        name
        value
      }
      directed: measure(measure: is_directed) {
        name
        value
      }
      planar: measure(measure: is_planar) {
        name
        value
      }
      connectivity: measure(measure: is_connected) {
        name
        value
      }
      node_connectivity: measure(measure: node_connectivity) {
        name
        value
      }
      threshold_graph: measure(measure: is_threshold_graph) {
        name
        value
      }
    }"""

    expected_response = {
        "empty": {
            "name": "is_empty",
            "value": 0
        },
        "directed": {
            "name": "is_directed",
            "value": 0
        },
        "planar": {
            "name": "is_planar",
            "value": 1
        },
        "connectivity": {
            "name": "is_connected",
            "value": 1
        },
        "node_connectivity": {
            "name": "node_connectivity",
            "value": 2
        },
        "threshold_graph": {
            "name": "is_threshold_graph",
            "value": 0
        }

    }

    # Register edges supplier function
    @graph_model.edge()
    def edge():
        for i in range(number_of_sides):
            yield {'source': i, 'target': i + 1}
        yield {'source': number_of_sides, 'target': 0}

    # act
    builder = graphinate.builders.GraphQLBuilder(graph_model)

    import strawberry
    schema: strawberry.Schema = builder.build(
        default_node_attributes=graphinate.builders.Builder.default_node_attributes
    )
    execution_result = schema.execute_sync(graphql_query)
    actual_response = execution_result.data

    # assert
    assert actual_response == expected_response
