"""
Consensus and Verification Module

Byzantine consensus algorithms and cryptographic verification
"""

from .byzantine import ByzantineConsensus
from .zkp import ZeroKnowledgeProof

__all__ = [
    "ByzantineConsensus",
    "ZeroKnowledgeProof",
]
