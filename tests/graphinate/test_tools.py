import dataclasses

import graphinate.tools.mutators
import pytest


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
