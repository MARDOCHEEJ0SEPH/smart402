"""
Cryptographic Utilities
"""

import hashlib
import hmac
from typing import Optional


def hash_data(data: str, algorithm: str = 'sha256') -> str:
    """
    Hash data using specified algorithm

    Args:
        data: Data to hash
        algorithm: Hash algorithm

    Returns:
        Hex digest
    """
    if algorithm == 'sha256':
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode()).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def generate_signature(data: str, key: str) -> str:
    """
    Generate HMAC signature

    Args:
        data: Data to sign
        key: Secret key

    Returns:
        Signature hex
    """
    signature = hmac.new(
        key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

    return signature


def verify_signature(data: str, signature: str, key: str) -> bool:
    """
    Verify HMAC signature

    Args:
        data: Original data
        signature: Signature to verify
        key: Secret key

    Returns:
        True if valid
    """
    expected = generate_signature(data, key)
    return hmac.compare_digest(signature, expected)


def keccak256(data: bytes) -> str:
    """
    Keccak256 hash (Ethereum-style)
    Simplified implementation

    Args:
        data: Data to hash

    Returns:
        Hash hex
    """
    # Note: Using SHA3-256 as approximation
    # Real implementation would use python-keccak
    return hashlib.sha3_256(data).hexdigest()
