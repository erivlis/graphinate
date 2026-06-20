import functools
import hashlib
import hmac
import os


@functools.cache
def _secret_key() -> str | None:
    """Retrieve the secret key from the environment variable."""
    return os.getenv("GRAPHINATE_SECRET_KEY")


def sign(payload: bytes, key: str) -> bytes:
    """Generate HMAC-SHA256 signature.

    Args:
        payload(bytes): The data to be signed.
        key(str): The secret key used for signing.

    """
    return hmac.new(key.encode(), payload, hashlib.sha256).digest()


def signed(payload: bytes, key: str) -> bytes:
    return sign(payload, key) + payload


def unsigned(signed_payload: bytes, key: str) -> bytes:
    if len(signed_payload) < 32:
        raise ValueError("Token too short")
    signature = signed_payload[:32]
    payload = signed_payload[32:]
    expected_signature = sign(payload, key)
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Invalid Signature - ID tampered with!")
    return payload
