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
    # Act
    actual = converters.value_to_infnum(case)

    # Assert
    assert actual == expected


@pytest.mark.parametrize(('case', 'expected'), inf_handling_cases)
def test_infnum_to_value(case, expected):
    # Act
    actual = converters.infnum_to_value(case)

    # Assert
    assert actual == expected


label_converter_cases = [
    (None, constants.DEFAULT_NODE_DELIMITER, None),
    (0, constants.DEFAULT_NODE_DELIMITER, "0"),
    (False, constants.DEFAULT_NODE_DELIMITER, "False"),
    ("", constants.DEFAULT_NODE_DELIMITER, ""),
    ("hello", constants.DEFAULT_NODE_DELIMITER, "hello"),
    (123, constants.DEFAULT_NODE_DELIMITER, "123"),
    (True, constants.DEFAULT_NODE_DELIMITER, "True"),
    ((1, "a", True), "-", "1-a-True"),
    (("node1", 1), "|", "node1|1"),
]


@pytest.mark.parametrize(('case', 'delimiter', 'expected'), label_converter_cases)
def test_label_converter(case, delimiter, expected):
    # Act
    actual = converters.label_converter(case, delimiter=delimiter)

    # Assert
    assert actual == expected


def test_encoding():
    # Arrange
    expected_edge = (("parent_a", "child_a"), ("parent_b", "child_b"))

    # Act
    edge_id = converters.encode_edge_id(expected_edge)
    actual_edge = converters.decode_edge_id(edge_id)

    # Assert
    assert actual_edge == expected_edge
