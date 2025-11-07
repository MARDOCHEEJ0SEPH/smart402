"""
Atomic Swap Handler

Hash Time-Locked Contract (HTLC) implementation
"""

import hashlib
import time
import secrets
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class HTLCContract:
    """Hash Time-Locked Contract"""
    hash_lock: str
    time_lock: float
    sender: str
    receiver: str
    amount: float
    secret: Optional[bytes] = None


class AtomicSwapHandler:
    """
    Atomic swap using HTLC

    HTLC conditions:
    1. H(secret) = hash (hash lock)
    2. now() < expiry (time lock)

    Security guarantee:
    P(successful_swap | honest) = 1
    """

    def __init__(self, lock_duration: int = 86400):
        """
        Initialize atomic swap handler

        Args:
            lock_duration: Lock duration in seconds (default 24h)
        """
        self.lock_duration = lock_duration
        self.active_htlcs: Dict[str, HTLCContract] = {}

    def create_htlc(
        self,
        sender: str,
        receiver: str,
        amount: float
    ) -> HTLCContract:
        """
        Create Hash Time-Locked Contract

        Args:
            sender: Sender address
            receiver: Receiver address
            amount: Amount to lock

        Returns:
            HTLC contract
        """
        # Generate secret
        secret = secrets.token_bytes(32)

        # Create hash lock
        hash_lock = hashlib.sha256(secret).hexdigest()

        # Create time lock
        time_lock = time.time() + self.lock_duration

        htlc = HTLCContract(
            hash_lock=hash_lock,
            time_lock=time_lock,
            sender=sender,
            receiver=receiver,
            amount=amount,
            secret=secret
        )

        # Store HTLC
        self.active_htlcs[hash_lock] = htlc

        return htlc

    def can_withdraw(
        self,
        hash_lock: str,
        provided_secret: bytes
    ) -> bool:
        """
        Check if withdrawal conditions are met

        Args:
            hash_lock: Hash lock identifier
            provided_secret: Secret to verify

        Returns:
            True if can withdraw
        """
        if hash_lock not in self.active_htlcs:
            return False

        htlc = self.active_htlcs[hash_lock]

        # Verify hash
        computed_hash = hashlib.sha256(provided_secret).hexdigest()
        if computed_hash != hash_lock:
            return False

        # Verify time
        if time.time() >= htlc.time_lock:
            return False

        return True

    def can_refund(self, hash_lock: str) -> bool:
        """
        Check if refund conditions are met

        Args:
            hash_lock: Hash lock identifier

        Returns:
            True if can refund
        """
        if hash_lock not in self.active_htlcs:
            return False

        htlc = self.active_htlcs[hash_lock]

        # Time lock must have expired
        return time.time() >= htlc.time_lock

    def withdraw(
        self,
        hash_lock: str,
        provided_secret: bytes
    ) -> Dict:
        """
        Withdraw from HTLC

        Args:
            hash_lock: Hash lock identifier
            provided_secret: Secret for verification

        Returns:
            Withdrawal result
        """
        if not self.can_withdraw(hash_lock, provided_secret):
            return {
                'success': False,
                'reason': 'withdrawal_conditions_not_met'
            }

        htlc = self.active_htlcs[hash_lock]

        # Remove from active
        del self.active_htlcs[hash_lock]

        return {
            'success': True,
            'amount': htlc.amount,
            'receiver': htlc.receiver
        }

    def refund(self, hash_lock: str) -> Dict:
        """
        Refund expired HTLC

        Args:
            hash_lock: Hash lock identifier

        Returns:
            Refund result
        """
        if not self.can_refund(hash_lock):
            return {
                'success': False,
                'reason': 'refund_conditions_not_met'
            }

        htlc = self.active_htlcs[hash_lock]

        # Remove from active
        del self.active_htlcs[hash_lock]

        return {
            'success': True,
            'amount': htlc.amount,
            'sender': htlc.sender
        }
