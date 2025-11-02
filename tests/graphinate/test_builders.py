from collections import Counter

import networkx as nx
import pytest

import graphinate
import graphinate.builders
from graphinate import GraphType
from graphinate.modeling import GraphModel, Multiplicity
from graphinate.typing import UniverseNode

graph_types = [
    (nx.Graph(), GraphType.Graph),
    (nx.DiGraph(), GraphType.DiGraph),
    (nx.MultiGraph(), GraphType.MultiGraph),
    (nx.MultiDiGraph(), GraphType.MultiDiGraph)
]


@pytest.mark.parametrize(('graph', 'expected_graph_type'), graph_types)
def test_returns_graph_type_for_graph(graph, expected_graph_type):
    # Act
    actual_graph_type = GraphType.of(graph)

    # Assert
    assert actual_graph_type == expected_graph_type


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


class DummyNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class DummyNodeModel:
    def __init__(self, uniqueness=True, label=None, type_='dummy', multiplicity=Multiplicity.ALL,
                 parent_type=UniverseNode, generator=None):
        self.uniqueness = uniqueness
        self.label = label
        self.type = type_
        self.multiplicity = multiplicity
        self.parent_type = parent_type
        self.generator = generator or (lambda **kwargs: [])


@pytest.fixture
def empty_graph_model():
    model = GraphModel(name="test")
    model._node_models = {}
    return model


@pytest.fixture
def builder_with_graph(empty_graph_model):
    builder = graphinate.builders.NetworkxBuilder(empty_graph_model)
    builder._graph = nx.Graph(name="test", node_types=Counter(), edge_types=Counter())
    return builder


def test_populate_nodes_adds_new_nodes_with_attributes(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n1', value=42)

    def generator(**kwargs):
        yield node

    node_model = DummyNodeModel(generator=generator)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    node_id = (node.key,)
    assert node_id in builder_with_graph._graph
    attrs = builder_with_graph._graph.nodes[node_id]
    assert attrs['label'] == node.key
    assert attrs['type'] == 'dummynode'
    assert attrs['value'] == [node.value]
    assert attrs['magnitude'] == 1
    assert attrs['lineage'] == [node.key]
    assert 'created' in attrs


def test_populate_nodes_adds_edges_for_non_universe_parent(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n1', value=1)

    def generator(**kwargs):
        yield node

    node_model = DummyNodeModel(generator=generator, parent_type='not_universe')
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    parent_node_id = builder_with_graph._parent_node_id(node_type_absolute_id)
    node_id = (node.key,)
    assert (parent_node_id, node_id) in builder_with_graph._graph.edges


def test_populate_nodes_handles_empty_generator(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')

    def generator(**kwargs):
        if False:
            yield

    node_model = DummyNodeModel(generator=generator)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    assert len(builder_with_graph._graph.nodes) == 0
    assert len(builder_with_graph._graph.edges) == 0


def test_populate_nodes_callable_label_assignment(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n1', value=7)

    def generator(**kwargs):
        yield node

    def label_fn(value):
        return f"label-{value}"

    node_model = DummyNodeModel(generator=generator, label=label_fn)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    node_id = (node.key,)
    assert builder_with_graph._graph.nodes[node_id]['label'] == "label-7"


def test_populate_nodes_handles_invalid_parent_node_id(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n1', value=1)

    def generator(**kwargs):
        yield node

    node_model = DummyNodeModel(generator=generator, parent_type=UniverseNode)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    node_id = (node.key,)
    # Should not create any edge since parent_type is UniverseNode
    assert len(builder_with_graph._graph.edges) == 0
    assert node_id in builder_with_graph._graph


def test_populate_nodes_adds_new_node(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n2', value=99)

    def generator(**kwargs):
        yield node

    node_model = DummyNodeModel(generator=generator)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    node_id = (node.key,)
    assert node_id in builder_with_graph._graph
    assert builder_with_graph._graph.nodes[node_id]['value'] == [99]


def test_populate_nodes_updates_existing_node(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n3', value=5)

    def generator(**kwargs):
        yield node
        yield node

    node_model = DummyNodeModel(generator=generator, multiplicity=Multiplicity.ALL)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    node_id = (node.key,)
    assert builder_with_graph._graph.nodes[node_id]['value'] == [5, 5]
    assert builder_with_graph._graph.nodes[node_id]['magnitude'] == 2


def test_populate_nodes_adds_edge_for_non_universe_parent(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n4', value=8)

    def generator(**kwargs):
        yield node

    node_model = DummyNodeModel(generator=generator, parent_type='not_universe')
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    parent_node_id = builder_with_graph._parent_node_id(node_type_absolute_id)
    node_id = (node.key,)
    assert (parent_node_id, node_id) in builder_with_graph._graph.edges


def test_populate_nodes_callable_label_returns_non_string(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')
    node = DummyNode(key='n5', value=123)

    def generator(**kwargs):
        yield node

    def label_fn(value):
        return 999  # Non-string label

    node_model = DummyNodeModel(generator=generator, label=label_fn)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    node_id = (node.key,)
    assert builder_with_graph._graph.nodes[node_id]['label'] == 999


def test_populate_nodes_empty_generator(builder_with_graph):
    node_type_absolute_id = ('parent', 'child')

    def generator(**kwargs):
        """Dummy generator that yields nothing"""
        return  # NOSONAR
        yield  # NOSONAR

    node_model = DummyNodeModel(generator=generator)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    assert len(builder_with_graph._graph.nodes) == 0


def test_populate_nodes_universe_node_parent_handling(builder_with_graph):
    node_type_absolute_id = (UniverseNode, 'child')
    node = DummyNode(key='n6', value=55)

    def generator(**kwargs):
        yield node

    node_model = DummyNodeModel(generator=generator, parent_type=UniverseNode)
    builder_with_graph.model._node_models = {node_type_absolute_id: [node_model]}
    builder_with_graph._populate_nodes(node_type_absolute_id)
    node_id = (node.key,)
    # Lineage should be (node.key,) and no edge should be created
    assert builder_with_graph._graph.nodes[node_id]['lineage'] == [node.key]
    assert len(builder_with_graph._graph.edges) == 0
