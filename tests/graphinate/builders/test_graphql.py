import pytest

import graphinate.builders


@pytest.mark.parametrize('execution_number', range(5))
def test_graphql_builder__map_graph_model(execution_number, map_graph_model, graphql_query):
    # arrange
    expected_country_count, expected_city_count, graph_model = map_graph_model
    expected_person_count = expected_city_count

    # act
    builder = graphinate.builders.GraphQLBuilder(graph_model)

    import strawberry
    schema: strawberry.Schema = builder.build()
    execution_result = schema.execute_sync(graphql_query)
    actual_graph = execution_result.data

    node_ids: set = {v['id'] for v in actual_graph['nodes']}
    edges = actual_graph['edges']
    edges_source_ids: set = {v['source']['id'] for v in edges}
    edges_targets_ids: set = {v['target']['id'] for v in edges}

    # assert
    assert actual_graph
    assert actual_graph['graph']
    assert actual_graph['nodes']
    assert actual_graph['edges']
    assert actual_graph['graph']['name'] == 'Map'
    node_types_counts = {c['name']: c['value'] for c in actual_graph['graph']['nodeTypeCounts']}
    assert node_types_counts['country'] == expected_country_count
    assert node_types_counts['city'] == expected_city_count
    assert len(actual_graph['nodes']) == expected_country_count + expected_city_count + expected_person_count
    assert edges_source_ids.issubset(node_ids)
    assert edges_targets_ids.issubset(node_ids)
    assert node_ids.issuperset(edges_source_ids)
    assert node_ids.issuperset(edges_targets_ids)


graphql_operations_cases = [
    ("""{
      empty: measure(measure: is_empty){...Details}
      directed: measure(measure: is_directed){...Details}
      planar: measure(measure: is_planar){...Details}
      connectivity: measure(measure: is_connected){...Details}
      node_connectivity: measure(measure: node_connectivity){...Details}
      threshold_graph: measure(measure: is_threshold_graph){...Details}
    }
    fragment Details on Measure {name value}
    """, {
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
    ((
         'query Graph {\n'
         'nodes(nodeId: "KDAsKQ==") {type label}\n'
         'edges(edgeId: "KCdLREFzS1E9PScsICdLREVzS1E9PScp") {type label}\n'
         '}'
     ),
     # noqa: E501
     {
         "nodes": [
             {
                 "type": "node",
                 "label": "0"
             }
         ],
         "edges": [
             {
                 "type": "edge",
                 "label": "0 ⟹ 1"
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
