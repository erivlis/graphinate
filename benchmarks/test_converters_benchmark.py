"""Benchmarks for the converters used on every GraphQL node and edge identifier."""

import itertools

import pytest

from graphinate.converters import (
    decode_edge_id,
    decode_node_id,
    edge_label_converter,
    encode_edge_id,
    encode_node_id,
    node_label_converter,
)

NODE_IDS = [(f'country-{i % 10}', f'city-{i}') for i in range(500)]
EDGE_IDS = [((source,), (target,)) for source, target in itertools.pairwise(NODE_IDS)]
ENCODED_NODE_IDS = [encode_node_id(node_id) for node_id in NODE_IDS]
ENCODED_EDGE_IDS = [encode_edge_id(edge_id) for edge_id in EDGE_IDS]


@pytest.mark.benchmark
def test_encode_node_id():
    for node_id in NODE_IDS:
        encode_node_id(node_id)


@pytest.mark.benchmark
def test_decode_node_id():
    for encoded in ENCODED_NODE_IDS:
        decode_node_id(encoded)


@pytest.mark.benchmark
def test_encode_edge_id():
    for edge_id in EDGE_IDS:
        encode_edge_id(edge_id)


@pytest.mark.benchmark
def test_decode_edge_id():
    for encoded in ENCODED_EDGE_IDS:
        decode_edge_id(encoded)


@pytest.mark.benchmark
def test_label_converters():
    for node_id in NODE_IDS:
        node_label_converter(node_id)

    for edge_id in EDGE_IDS:
        edge_label_converter(edge_id)
