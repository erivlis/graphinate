import base64
import json


def encode_custom(obj):
    if isinstance(obj, tuple):
        return {'__tuple__': True, 'items': [encode_custom(item) for item in obj]}
    if isinstance(obj, set):
        return {'__set__': True, 'items': [encode_custom(item) for item in obj]}
    if isinstance(obj, frozenset):
        return {'__frozenset__': True, 'items': [encode_custom(item) for item in obj]}
    if isinstance(obj, complex):
        return {'__complex__': True, 'real': obj.real, 'imag': obj.imag}
    if isinstance(obj, bytes):
        return {'__bytes__': True, 'data': base64.urlsafe_b64encode(obj).decode('utf-8')}
    if isinstance(obj, list):
        return [encode_custom(item) for item in obj]
    if isinstance(obj, dict):
        return {key: encode_custom(value) for key, value in obj.items()}
    return obj

def decode_custom(dct):
    if '__tuple__' in dct:
        return tuple(decode_custom(item) for item in dct['items'])
    if '__set__' in dct:
        return {decode_custom(item) for item in dct['items']}
    if '__frozenset__' in dct:
        return frozenset(decode_custom(item) for item in dct['items'])
    if '__complex__' in dct:
        return complex(dct['real'], dct['imag'])
    if '__bytes__' in dct:
        return base64.urlsafe_b64decode(dct['data'].encode('utf-8'))
    if isinstance(dct, list):
        return [decode_custom(item) for item in dct]
    if isinstance(dct, dict):
        return {key: decode_custom(value) for key, value in dct.items()}
    return dct

# Example usage
data = {
    'nested_tuple': ((1, 2), (3, 4)),
    'nested_set': {frozenset({1, 2}), frozenset({3, 4})},
    'complex_number': 3 + 4j,
    'byte_data': b'hello'
}

# Encode
encoded_data = json.dumps(data, default=encode_custom)
print(encoded_data)

# Decode
decoded_data = json.loads(encoded_data, object_hook=decode_custom)
print(decoded_data)
