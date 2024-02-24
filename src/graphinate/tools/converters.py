import decimal
import math
from types import MappingProxyType
from typing import NewType, Union

InfNumber = NewType("InfNumber", Union[float, int, decimal.Decimal])

INFINITY_MAPPER = MappingProxyType({
    'Infinity': math.inf,
    '-Infinity': -math.inf
})

MATH_INF_MAPPER = MappingProxyType({
    math.inf: 'Infinity',
    -math.inf: '-Infinity'
})


def str_to_infnum(value: str):
    return INFINITY_MAPPER.get(value, value)


def infnum_to_str(value: InfNumber):
    return MATH_INF_MAPPER.get(value, value)


__all__ = ['InfNumber', 'infnum_to_str', 'str_to_infnum']
