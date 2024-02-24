import dataclasses
import math

import pytest

import graphinate.tools.mutators
from graphinate.tools import converters


@dataclasses.dataclass
class Data:
    a: int
    b: str


data = Data(1, 'alpha')

dictify_cases = [
    ([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
    ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
    ((1, 2, 3, 4, 'a'), [1, 2, 3, 4, 'a']),
    (data, {'a': 1, 'b': 'alpha'})
]


@pytest.mark.parametrize(('case', 'expected'), dictify_cases)
def test_dictify(case, expected):
    actual = graphinate.tools.mutators.dictify(case)
    assert actual == expected


dictify_value_as_str_cases = [
    ([0.5, 0.5, 0.5], ['0.5', '0.5', '0.5']),
    ({'a': 1, 'b': 2}, {'a': '1', 'b': '2'}),
    ((1, 2, 3, 4, 'a'), ['1', '2', '3', '4', 'a']),
    (data, {'a': '1', 'b': 'alpha'})
]


@pytest.mark.parametrize(('case', 'expected'), dictify_value_as_str_cases)
def test_dictify__value_to_str(case, expected):
    actual = graphinate.tools.mutators.dictify(case, value_converter=str)
    assert actual == expected


@pytest.mark.parametrize(('case', 'expected'),
                         [('1', '1'), ('1.1', '1.1'), (1, 1), (1.1, 1.1), (0, 0), (True, True), ('Infinity', math.inf),
                          ('-Infinity', -math.inf), ('+Infinity', math.inf)])
def test_value_to_infnum(case, expected):
    # act
    actual = converters.value_to_infnum(case)

    # assert
    assert actual == expected


@pytest.mark.parametrize(('case', 'expected'),
                         [('1', '1'), ('1.1', '1.1'), (1, 1), (1.1, 1.1), (0, 0), (True, True), (math.inf, 'Infinity'),
                          (-math.inf, '-Infinity')])
def test_infnum_to_value(case, expected):
    # act
    actual = converters.infnum_to_value(case)

    # assert
    assert actual == expected
