"""
Smart402 Python SDK

Universal Protocol for AI-Native Smart Contracts

Example:
    >>> from smart402 import Smart402
    >>>
    >>> contract = await Smart402.create({
    ...     'type': 'saas-subscription',
    ...     'parties': ['vendor@example.com', 'customer@example.com'],
    ...     'payment': {
    ...         'amount': 99,
    ...         'frequency': 'monthly',
    ...         'token': 'USDC'
    ...     }
    ... })
    >>>
    >>> await contract.deploy(network='polygon')
"""

from .core.smart402 import Smart402
from .core.contract import Contract
from .aeo.engine import AEOEngine
from .llmo.engine import LLMOEngine
from .x402.client import X402Client

__version__ = "1.0.0"
__all__ = [
    "Smart402",
    "Contract",
    "AEOEngine",
    "LLMOEngine",
    "X402Client",
]
