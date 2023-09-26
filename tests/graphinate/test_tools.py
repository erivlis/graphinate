import dataclasses
import sys

import pytest

import graphinate.tools.mutators
from graphinate.tools.importer import ImportFromStringError, import_from_string


@dataclasses.dataclass
class Data:
    a: int
    b: str


data = Data(1, 'alpha')

cases = [
    ([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
    ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
    ((1, 2, 3, 4, 'a'), [1, 2, 3, 4, 'a']),
    (data, {'a': 1, 'b': 'alpha'})
]


@pytest.mark.parametrize(('case', 'expected'), cases)
def test_dictify(case, expected):
    actual = graphinate.tools.mutators.dictify(case)
    assert actual == expected


value_as_str_cases = [
    ([0.5, 0.5, 0.5], ['0.5', '0.5', '0.5']),
    ({'a': 1, 'b': 2}, {'a': '1', 'b': '2'}),
    ((1, 2, 3, 4, 'a'), ['1', '2', '3', '4', 'a']),
    (data, {'a': '1', 'b': 'alpha'})
]


@pytest.mark.parametrize(('case', 'expected'), value_as_str_cases)
def test_dictify__value_to_str(case, expected):
    actual = graphinate.tools.mutators.dictify(case, value_converter=str)
    assert actual == expected


def test_import_from_string():
    sys.path.append('examples/math')
    actual = import_from_string("polygonal_graph:model")
    assert isinstance(actual, graphinate.GraphModel)
    assert actual.name == "Octagonal Graph"


import_from_string_error_cases = [
    ("does_not_exist:model", "Could not import module 'does_not_exist'."),
    ("polygonal_graph:does_not_exist", "Attribute 'does_not_exist' not found in module 'polygonal_graph'."),
    ("wrong_format", "Import string 'wrong_format' must be in format '<module>:<attribute>'.")
]


@pytest.mark.parametrize(('case', 'message'), import_from_string_error_cases)
def test_import_from_string__error(case, message):
    sys.path.append('examples/math')
    with pytest.raises(ImportFromStringError, match=message):
        _ = import_from_string(case)


import_from_string_not_str_cases = [
    0,
    None
]


@pytest.mark.parametrize('case', import_from_string_not_str_cases)
def test_import_from_string__not_str(case):
    actual = import_from_string(case)
    assert actual == case
