import math

import pytest

from graphinate import constants, converters

base_cases = [
    ('1', '1'),
    ('1.1', '1.1'),
    (1, 1),
    (1.1, 1.1),
    (0, 0),
    (True, True)
]

value_handling_cases = [
    *base_cases,
    ('Infinity', math.inf),
    ('-Infinity', -math.inf),
    ('+Infinity', math.inf)
]

inf_handling_cases = [
    *base_cases,
    (math.inf, 'Infinity'),
    (-math.inf, '-Infinity')
]


@pytest.mark.parametrize(('case', 'expected'), value_handling_cases)
def test_value_to_infnum(case, expected):
    # act
    actual = converters.value_to_infnum(case)

    # assert
    assert actual == expected


@pytest.mark.parametrize(('case', 'expected'), inf_handling_cases)
def test_infnum_to_value(case, expected):
    # act
    actual = converters.infnum_to_value(case)

    # assert
    assert actual == expected


@pytest.mark.parametrize('case', [0, None, "", False])
def test_label_converter__value__falsy(case):
    actual = converters.label_converter(case, delimiter=constants.DEFAULT_NODE_DELIMITER)
    assert actual == case


def test_encoding():
    expected_edge = (("parent_a", "child_a"), ("parent_b", "child_b"))

    edge_id = converters.encode_edge_id(expected_edge)
    actual_edge = converters.decode_edge_id(edge_id)

    assert actual_edge == expected_edge
