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


def test_secure_encoding_decoding(monkeypatch):
    import base64
    from graphinate._secure import _secret_key

    # Ensure cache is clear at the beginning
    _secret_key.cache_clear()

    test_payload = (('node1', 'value1'), ('node2', 'value2'))

    # Encode without secret key
    unsigned_id = converters.encode(test_payload)

    # Enable signature protection
    monkeypatch.setenv('GRAPHINATE_SECRET_KEY', 'test-secret-key-12345')
    _secret_key.cache_clear()

    # Encode with secret key
    signed_id = converters.encode(test_payload)

    # Assert they are different
    assert signed_id != unsigned_id

    # Decode with secret key
    decoded_payload = converters.decode(signed_id)
    assert decoded_payload == test_payload

    # Tamper with the signed ID (change a character in base64 string)
    raw_bytes = base64.urlsafe_b64decode(signed_id.encode('utf-8'))
    # Tamper with the first byte (which is part of the signature)
    tampered_bytes = bytes([raw_bytes[0] ^ 0xFF]) + raw_bytes[1:]
    tampered_id = base64.urlsafe_b64encode(tampered_bytes).decode('utf-8')

    with pytest.raises(ValueError, match='Invalid Signature - ID tampered with!'):
        converters.decode(tampered_id)

    # Test short token
    short_id = base64.urlsafe_b64encode(b'too-short').decode('utf-8')
    with pytest.raises(ValueError, match='Token too short'):
        converters.decode(short_id)

    # Cleanup environment and cache
    monkeypatch.delenv('GRAPHINATE_SECRET_KEY', raising=False)
    _secret_key.cache_clear()

