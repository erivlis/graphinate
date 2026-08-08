"""Shared fixtures for the Graphinate benchmark suite.

The models defined here are deterministic (no randomness, no I/O) so that
measurements stay comparable from one run to the next.
"""

import networkx as nx
import pytest

import graphinate
from graphinate.builders import NetworkxBuilder

COUNTRY_COUNT = 10
CITY_COUNT = 200
MESH_NODE_COUNT = 400
MESH_DEGREE = 3


def hierarchical_model(country_count: int = COUNTRY_COUNT, city_count: int = CITY_COUNT) -> graphinate.GraphModel:
    """A two level parent/child model, exercising nested node generation."""
    countries = tuple(f'country-{i}' for i in range(country_count))
    cities = {f'city-{i}': countries[i % country_count] for i in range(city_count)}

    graph_model = graphinate.model(name='Map')

    @graph_model.node(unique=False)
    def country(country_id=None, **kwargs):
        if country_id is not None and country_id in countries:
            yield country_id
        else:
            yield from countries

    @graph_model.node(parent_type='country', unique=False)
    def city(country_id=None, city_id=None, **kwargs):
        if city_id is not None:
            if cities.get(city_id) == country_id or country_id is None:
                yield city_id
        elif country_id is None:
            yield from cities
        else:
            yield from (k for k, v in cities.items() if v == country_id)

    return graph_model


def mesh_model(node_count: int = MESH_NODE_COUNT, degree: int = MESH_DEGREE) -> graphinate.GraphModel:
    """An edge only model producing a circulant graph, exercising edge population."""
    graph_model = graphinate.model(name='Mesh')

    @graph_model.edge()
    def edge():
        for i in range(node_count):
            for offset in range(1, degree + 1):
                yield {'source': i, 'target': (i + offset) % node_count}

    return graph_model


@pytest.fixture
def hierarchical_graph_model() -> graphinate.GraphModel:
    return hierarchical_model()


@pytest.fixture
def mesh_graph_model() -> graphinate.GraphModel:
    return mesh_model()


@pytest.fixture
def mesh_graph() -> nx.Graph:
    """A materialized NetworkX graph, used to benchmark post-processing steps."""
    return NetworkxBuilder(mesh_model()).build()
