import ast
import base64
import decimal
import math
from types import MappingProxyType
from typing import Any, Union

import strawberry

from ._secure import _secret_key, signed, unsigned
from .constants import DEFAULT_EDGE_DELIMITER, DEFAULT_NODE_DELIMITER

__all__ = [
    'InfNumber',
    'decode',
    'decode_edge_id',
    'decode_node_id',
    'edge_label_converter',
    'encode',
    'encode_edge_id',
    'encode_node_id',
    'infnum_to_value',
    'label_converter',
    'node_label_converter',
    'value_to_infnum',
]

InfNumber = Union[float, int, decimal.Decimal]

INFINITY_MAPPING: MappingProxyType[str, InfNumber] = MappingProxyType({
    'Infinity': math.inf,
    '+Infinity': math.inf,
    '-Infinity': -math.inf
})

MATH_INF_MAPPING: MappingProxyType[InfNumber, str] = MappingProxyType({
    math.inf: 'Infinity',
    -math.inf: '-Infinity'
})


def value_to_infnum(value: str | InfNumber) -> InfNumber:
    return INFINITY_MAPPING.get(value, value)


def infnum_to_value(value: InfNumber) -> InfNumber | str:
    return MATH_INF_MAPPING.get(value, value)


def label_converter(value: Any, delimiter: str) -> str | None:
    if value is not None:
        return delimiter.join(str(v) for v in value) if isinstance(value, tuple) else str(value)
    return value


def node_label_converter(value: Any) -> str | None:
    return label_converter(value, delimiter=DEFAULT_NODE_DELIMITER)


def edge_label_converter(value: Any) -> str | None:
    return label_converter(tuple(node_label_converter(n) for n in value), delimiter=DEFAULT_EDGE_DELIMITER)


def encode(value: Any, encoding: str = 'utf-8') -> str:
    obj_s: str = repr(value)
    obj_b: bytes = obj_s.encode(encoding)

    if key := _secret_key():
        obj_b = signed(obj_b, key)

    enc_b: bytes = base64.urlsafe_b64encode(obj_b)
    enc_s: str = enc_b.decode(encoding)
    return enc_s


def decode(value: str, encoding: str = 'utf-8') -> Any:
    enc_b: bytes = value.encode(encoding)
    obj_b: bytes = base64.urlsafe_b64decode(enc_b)

    if key := _secret_key():
        obj_b = unsigned(obj_b, key)

    obj_s: str = obj_b.decode(encoding)
    obj: Any = ast.literal_eval(obj_s)
    return obj


def encode_node_id(node_id: tuple, encoding: str = 'utf-8') -> str:
    return encode(node_id, encoding)


def decode_node_id(encoded_node_id: strawberry.ID, encoding: str = 'utf-8') -> tuple[str, ...]:
    return decode(encoded_node_id, encoding)


def encode_edge_id(edge_id: tuple, encoding: str = 'utf-8') -> str:
    return encode(edge_id, encoding)


def decode_edge_id(encoded_edge_id: strawberry.ID, encoding: str = 'utf-8') -> tuple:
    return decode(encoded_edge_id, encoding)
