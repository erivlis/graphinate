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


def test_networkx_builder_repeating_nodes():
    # arrange
    name = 'Repeating Nodes'
    graph_model = graphinate.GraphModel(name=name)

    @graph_model.node()
    def node():
        for i in range(5):
            yield i
            yield i

    # act
    builder = graphinate.builders.NetworkxBuilder(graph_model)
    graph: nx.Graph = builder.build()

    # assert
    assert isinstance(graph, nx.Graph)
    assert graph.graph['name'] == name
    assert all(graph.nodes[n]['magnitude'] == 2 for n in graph)


@pytest.mark.parametrize('weight', [1.0, 1.5])
def test_networkx_builder_repeating_edges(weight):
    # arrange
    name = 'Repeating Edges'
    graph_model = graphinate.GraphModel(name=name)

    @graph_model.edge(weight=weight)
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
    assert all(m == weight * 2 for *_, m in graph.edges.data('weight'))


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


graphql_operations_cases = [
    ("""{
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
    }""", {
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

    }),
    ("""
    query Graph {
      nodes(nodeId: "H4sIAFs7E2UC/2tgmcrKAAHeDK1T9ADQP1FHEAAAAA==") {type label}
      edges(edgeId: "H4sIAFs7E2UC/2tgmZrIAAE9Oh4mxZ6ObsXmrkahzvpGJem5yUXejo4eqS7ehiGWji6BAYZuHq6OIGBrOwW38iywcmfDcH9jfbjytil6AHhudC5sAAAA") {type label}
    }
    """, {
        "nodes": [
            {
                "type": "node",
                "label": "0"
            }
        ],
        "edges": [
            {
                "type": "edge",
                "label": "{'source': 0, 'target': 1}"
            }
        ]
    }),
    ("""
    query Graph {
      nodes(nodeId: "H4sIAFs7E2UC/2tgmcrKAAHeDK1T9ADQP1FHEAAAAA==") {type label}
      edges(edgeId: "H4sIAFs7E2UC/2tgmZrIAAE9Oh4mxZ6ObsXmrkahzvpGJem5yUXejo4eqS7ehiGWji6BAYZuHq6OIGBrOwW38iywcmfDcH9jfbjytil6AHhudC5sAAAA") {type label}
    }
    """, {
        "nodes": [
            {
                "type": "node",
                "label": "0"
            }
        ],
        "edges": [
            {
                "type": "edge",
                "label": "{'source': 0, 'target': 1}"
            }
        ]
    }),
    ("mutation {refresh}", {'refresh': True})
]


@pytest.mark.parametrize(('graphql_query', 'expected_response'), graphql_operations_cases)
def test_graphql_builder_query(octagonal_graph_model, graphql_query, expected_response):
    # act
    builder = graphinate.builders.GraphQLBuilder(octagonal_graph_model)

    import strawberry
    schema: strawberry.Schema = builder.build(
        default_node_attributes=graphinate.builders.Builder.default_node_attributes
    )
    execution_result = schema.execute_sync(graphql_query)
    actual_response = execution_result.data

    # assert
    assert actual_response == expected_response


def test_graphql_builder__ast_model__graph_query(ast_graph_model, graphql_query):
    # act
    builder = graphinate.builders.GraphQLBuilder(ast_graph_model)
    import strawberry
    schema: strawberry.Schema = builder.build()
    execution_result = schema.execute_sync(graphql_query)
    actual_graph = execution_result.data

    # assert
    assert actual_graph
    assert actual_graph['graph']
    assert actual_graph['nodes']
    assert actual_graph['edges']
    assert actual_graph['graph']['name'] == 'AST Graph'
    node_types_counts = {c['name']: c['value'] for c in actual_graph['graph']['nodeTypeCounts']}
    assert node_types_counts
