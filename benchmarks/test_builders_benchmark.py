"""Benchmarks for the builders, the core of Graphinate's data pipeline."""

import networkx as nx
import pytest
import strawberry

import graphinate
from graphinate import GraphType
from graphinate.builders import D3Builder, GraphQLBuilder, MermaidBuilder, NetworkxBuilder

GRAPHQL_QUERY = """
query Graph {
  graph {
    name
    nodeTypeCounts { name value }
    edgeTypeCounts { name value }
    nodeCount
    edgeCount
    order
    size
  }
  nodes { id type label color }
  edges { source { id } target { id } type label weight }
}
"""


@pytest.mark.benchmark
def test_networkx_builder__mesh(mesh_graph_model):
    graph = NetworkxBuilder(mesh_graph_model).build()
    assert graph.number_of_nodes() > 0


@pytest.mark.benchmark
def test_networkx_builder__hierarchical(hierarchical_graph_model):
    graph = NetworkxBuilder(hierarchical_graph_model).build()
    assert graph.number_of_nodes() > 0


@pytest.mark.benchmark
def test_networkx_builder__digraph(mesh_graph_model):
    graph = NetworkxBuilder(mesh_graph_model, graph_type=GraphType.DiGraph).build()
    assert isinstance(graph, nx.DiGraph)


@pytest.mark.benchmark
def test_d3_builder__python(mesh_graph_model):
    d3_graph = D3Builder(mesh_graph_model).build()
    assert d3_graph['nodes']


@pytest.mark.benchmark
def test_d3_builder__json(mesh_graph_model):
    d3_graph = D3Builder(mesh_graph_model).build(values_format='json')
    assert d3_graph['nodes']


@pytest.mark.benchmark
def test_d3_builder__from_networkx(mesh_graph):
    d3_graph = D3Builder.from_networkx(mesh_graph)
    assert d3_graph['nodes']


@pytest.mark.benchmark
def test_mermaid_builder(mesh_graph_model):
    diagram = MermaidBuilder(mesh_graph_model).build()
    assert diagram


@pytest.mark.benchmark
def test_graphql_builder__schema(hierarchical_graph_model):
    schema = GraphQLBuilder(hierarchical_graph_model).build()
    assert isinstance(schema, strawberry.Schema)


def test_graphql_builder__query(benchmark, hierarchical_graph_model):
    schema: strawberry.Schema = GraphQLBuilder(hierarchical_graph_model).build()

    result = benchmark(schema.execute_sync, GRAPHQL_QUERY)

    assert result.errors is None
    assert result.data['nodes']


@pytest.mark.benchmark
def test_build_facade(mesh_graph_model):
    graph = graphinate.build(NetworkxBuilder, mesh_graph_model)
    assert graph.number_of_nodes() > 0
