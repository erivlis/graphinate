"""Benchmarks for the modeling layer: element creation and model registration."""

import operator

import pytest

from graphinate.modeling import GraphModel, elements, extractor

PAYLOADS = [{'id': i, 'name': f'item-{i}', 'kind': 'even' if i % 2 == 0 else 'odd'} for i in range(2000)]


@pytest.mark.benchmark
def test_elements__static_type():
    generated = elements(PAYLOADS, 'item', key=operator.itemgetter('id'), label=operator.itemgetter('name'))
    assert sum(1 for _ in generated) == len(PAYLOADS)


@pytest.mark.benchmark
def test_elements__dynamic_type():
    generated = elements(
        PAYLOADS,
        operator.itemgetter('kind'),
        key=operator.itemgetter('id'),
        label=operator.itemgetter('name'),
    )
    assert sum(1 for _ in generated) == len(PAYLOADS)


@pytest.mark.benchmark
def test_extractor():
    for payload in PAYLOADS:
        extractor(payload, 'name')
        extractor(payload, operator.itemgetter('id'))
        extractor(payload)


@pytest.mark.benchmark
def test_model_registration():
    graph_model = GraphModel(name='Registration')

    @graph_model.node()
    def country(**kwargs):
        yield from ()

    @graph_model.node(parent_type='country')
    def city(country_id=None, **kwargs):
        yield from ()

    @graph_model.edge()
    def edge(**kwargs):
        yield from ()

    assert graph_model.node_types == {'country', 'city'}
