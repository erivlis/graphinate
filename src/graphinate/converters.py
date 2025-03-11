import ast
import base64
import decimal
import math
from types import MappingProxyType
from typing import Any, NewType, Union

import strawberry

from .constants import DEFAULT_EDGE_DELIMITER, DEFAULT_NODE_DELIMITER

__all__ = [
    'InfNumber',
    'decode_edge_id',
    'decode_id',
    'edge_label_converter',
    'encode_edge_id',
    'encode_id',
    'infnum_to_value',
    'label_converter',
    'node_label_converter',
    'value_to_infnum',
]

InfNumber = NewType("InfNumber", Union[float, int, decimal.Decimal])

INFINITY_MAPPING = MappingProxyType({
    'Infinity': math.inf,
    '+Infinity': math.inf,
    '-Infinity': -math.inf
})

MATH_INF_MAPPING = MappingProxyType({
    math.inf: 'Infinity',
    -math.inf: '-Infinity'
})


def value_to_infnum(value: any) -> InfNumber:
    return INFINITY_MAPPING.get(value, value)


def infnum_to_value(value: InfNumber):
    return MATH_INF_MAPPING.get(value, value)


def label_converter(value, delimiter: str):
    if value:
        return delimiter.join(str(v) for v in value) if isinstance(value, tuple) else str(value)

    return value


def node_label_converter(value):
    return label_converter(value, delimiter=DEFAULT_NODE_DELIMITER)


def edge_label_converter(value):
    return label_converter(tuple(node_label_converter(n) for n in value), delimiter=DEFAULT_EDGE_DELIMITER)


def encode(value: Any, encoding: str = 'utf-8') -> str:
    obj_s: str = repr(value)
    obj_b: bytes = obj_s.encode(encoding)
    enc_b: bytes = base64.urlsafe_b64encode(obj_b)
    enc_s: str = enc_b.decode(encoding)
    return enc_s


def decode(value: str, encoding: str = 'utf-8') -> Any:
    enc_b: bytes = value.encode(encoding)
    obj_b: bytes = base64.urlsafe_b64decode(enc_b)
    obj_s: str = obj_b.decode(encoding)
    obj: Any = ast.literal_eval(obj_s)
    return obj


def encode_id(graph_node_id: tuple,
              encoding: str = 'utf-8') -> str:
    return encode(graph_node_id, encoding)


def decode_id(graphql_node_id: strawberry.ID,
              encoding: str = 'utf-8') -> tuple[str, ...]:
    return decode(graphql_node_id, encoding)


def encode_edge_id(edge: tuple, encoding: str = 'utf-8'):
    encoded_edge = tuple(encode_id(n, encoding) for n in edge)
    return encode_id(encoded_edge, encoding)


def decode_edge_id(graphql_edge_id: strawberry.ID, encoding: str = 'utf-8'):
    encoded_edge: tuple = decode_id(graphql_edge_id, encoding)
    return tuple(decode_id(enc_node) for enc_node in encoded_edge)
