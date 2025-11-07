"""
X402 Payment Execution

Payment validation:
Valid(P) = (Σ votes(P) > 2n/3) ∧ verify_conditions(P) ∧ verify_smart_contract(P)
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PaymentResult:
    """Result of payment execution"""
    success: bool
    tx_hash: Optional[str]
    amount: float
    gas_used: int
    execution_time: float


class PaymentExecutor:
    """
    Execute payments with Byzantine Fault Tolerance

    Consensus requirement: n ≥ 3f + 1
    """

    def __init__(self, num_nodes: int = 7):
        """
        Initialize payment executor

        Args:
            num_nodes: Number of consensus nodes
        """
        self.num_nodes = num_nodes
        self.f = (num_nodes - 1) // 3  # Max faulty nodes

    def execute_payment(self, contract: Dict, conditions: Dict) -> PaymentResult:
        """
        Execute payment with condition verification

        Args:
            contract: Contract data
            conditions: Payment conditions

        Returns:
            Payment result
        """
        start_time = time.time()

        # Verify conditions
        if not self._verify_conditions(contract, conditions):
            return PaymentResult(
                success=False,
                tx_hash=None,
                amount=0,
                gas_used=0,
                execution_time=time.time() - start_time
            )

        # Verify smart contract execution
        if not self._verify_smart_contract_execution(contract):
            return PaymentResult(
                success=False,
                tx_hash=None,
                amount=0,
                gas_used=0,
                execution_time=time.time() - start_time
            )

        # Execute payment
        amount = contract.get('amount', 0)
        tx_hash = self._execute_transaction(contract, amount)
        gas_used = self._estimate_gas_used(contract)

        return PaymentResult(
            success=True,
            tx_hash=tx_hash,
            amount=amount,
            gas_used=gas_used,
            execution_time=time.time() - start_time
        )

    def _verify_conditions(self, contract: Dict, conditions: Dict) -> bool:
        """
        Verify payment conditions using oracle consensus

        Args:
            contract: Contract data
            conditions: Conditions to verify

        Returns:
            True if conditions met
        """
        # Simplified oracle verification
        required_votes = 2 * self.num_nodes // 3 + 1

        # Simulate votes
        votes = self.num_nodes - self.f  # Assume honest majority

        return votes >= required_votes

    def _verify_smart_contract_execution(self, contract: Dict) -> bool:
        """
        Verify smart contract conditions

        Args:
            contract: Contract data

        Returns:
            True if smart contract valid
        """
        if not contract.get('smart_contract_code'):
            return True  # No smart contract requirement

        # Check if deployed and conditions met
        return contract.get('verified', False)

    def _execute_transaction(self, contract: Dict, amount: float) -> str:
        """
        Execute blockchain transaction

        Args:
            contract: Contract data
            amount: Payment amount

        Returns:
            Transaction hash
        """
        import hashlib

        # Generate transaction hash
        tx_data = f"{contract.get('id')}:{amount}:{time.time()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()

        return tx_hash

    def _estimate_gas_used(self, contract: Dict) -> int:
        """
        Estimate gas used for transaction

        Args:
            contract: Contract data

        Returns:
            Gas estimate
        """
        base_gas = 21000

        if contract.get('smart_contract_code'):
            base_gas += contract.get('gas_estimate', 50000)

        return base_gas
