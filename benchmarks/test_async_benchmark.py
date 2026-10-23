"""Benchmarks for asynchronous graph execution (abuild) and concurrency."""

import asyncio

import pytest

import graphinate
from graphinate.builders import D3Builder, NetworkxBuilder


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_networkx_builder__async_mesh(async_mesh_graph_model):
    graph = await graphinate.abuild(NetworkxBuilder, async_mesh_graph_model)
    assert graph.number_of_nodes() > 0


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_networkx_builder__async_hierarchical(async_hierarchical_graph_model):
    graph = await graphinate.abuild(NetworkxBuilder, async_hierarchical_graph_model)
    assert graph.number_of_nodes() > 0


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_d3_builder__async_mesh(async_mesh_graph_model):
    d3_graph = await graphinate.abuild(D3Builder, async_mesh_graph_model)
    assert d3_graph['nodes']


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_async_concurrency__multi_model(async_mesh_graph_model, async_hierarchical_graph_model):
    graphs = await asyncio.gather(
        graphinate.abuild(NetworkxBuilder, async_mesh_graph_model),
        graphinate.abuild(NetworkxBuilder, async_hierarchical_graph_model),
        graphinate.abuild(D3Builder, async_mesh_graph_model),
    )
    assert len(graphs) == 3
