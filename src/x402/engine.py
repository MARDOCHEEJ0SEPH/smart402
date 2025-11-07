"""
X402 Engine
Main orchestration for X402 Protocol
"""

from typing import Dict, List, Optional
from .payment import PaymentExecutor
from .atomic_swap import AtomicSwapHandler
from .routing import PaymentRouter


class X402Engine:
    """
    Main X402 Engine integrating payment execution,
    atomic swaps, and routing optimization
    """

    def __init__(self):
        """Initialize X402 engine"""
        self.payment_executor = PaymentExecutor()
        self.atomic_swap = AtomicSwapHandler()
        self.router = PaymentRouter()

    async def optimize_execution(
        self,
        contracts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Optimize and execute payments

        Args:
            contracts: Contracts to execute

        Returns:
            Executed contracts
        """
        if contracts is None:
            contracts = []

        executed = []

        for contract in contracts:
            # Find optimal route
            source = contract.get('source_network', 'ethereum')
            dest = contract.get('dest_network', 'ethereum')
            amount = contract.get('amount', 0)

            route = self.router.find_optimal_route(source, dest, amount)

            if route is None:
                contract['execution_status'] = 'failed'
                contract['error'] = 'no_route_found'
                continue

            # Execute payment
            result = self.payment_executor.execute_payment(
                contract,
                conditions={}
            )

            if not result.success:
                contract['execution_status'] = 'failed'
                contract['error'] = 'payment_execution_failed'
                continue

            # Add execution details
            contract['execution_status'] = 'success'
            contract['tx_hash'] = result.tx_hash
            contract['gas_used'] = result.gas_used
            contract['execution_time'] = result.execution_time
            contract['route'] = route.path
            contract['route_cost'] = route.cost

            executed.append(contract)

        return executed
