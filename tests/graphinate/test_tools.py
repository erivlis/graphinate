import dataclasses

import graphinate.tools.mutators
import pytest


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
