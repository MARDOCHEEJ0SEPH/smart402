"""
Smart402 - Complete Algorithmic Framework
AEO + LLMO + SCC + X402 Protocol Integration

This package provides a comprehensive framework for:
- Answer Engine Optimization (AEO)
- Large Language Model Optimization (LLMO)
- Smart Contract Compilation (SCC)
- X402 Payment Protocol
"""

__version__ = "1.0.0"
__author__ = "Smart402 Team"

from .core.state_machine import Smart402StateMachine
from .core.orchestrator import Smart402Orchestrator

__all__ = [
    "Smart402StateMachine",
    "Smart402Orchestrator",
]
