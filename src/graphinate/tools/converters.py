import decimal
import math
from types import MappingProxyType
from typing import NewType, Union

InfNumber = NewType("InfNumber", Union[float, int, decimal.Decimal])

INFINITY_MAPPER = MappingProxyType({
    'Infinity': math.inf,
    '+Infinity': math.inf,
    '-Infinity': -math.inf
})

MATH_INF_MAPPER = MappingProxyType({
    math.inf: 'Infinity',
    -math.inf: '-Infinity'
})


def value_to_infnum(value: any) -> InfNumber:
    return INFINITY_MAPPER.get(value, value)


def infnum_to_value(value: InfNumber):
    return MATH_INF_MAPPER.get(value, value)


__all__ = ['InfNumber', 'infnum_to_value', 'value_to_infnum']
