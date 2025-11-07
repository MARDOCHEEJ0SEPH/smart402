"""
Payment Routing Optimization
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PaymentRoute:
    """Payment route information"""
    path: List[str]
    cost: float
    estimated_time: float
    liquidity_available: float


class PaymentRouter:
    """
    Optimize payment routing using Dijkstra with dynamic weights

    Cost function:
    C(path) = Σ(gas_cost(e) + slippage(e) + time_cost(e))
    """

    def __init__(self):
        """Initialize payment router"""
        self.networks = {
            'ethereum': {'gas_price': 50, 'speed': 12},
            'polygon': {'gas_price': 1, 'speed': 2},
            'arbitrum': {'gas_price': 0.5, 'speed': 1},
            'optimism': {'gas_price': 0.3, 'speed': 1}
        }

        self.liquidity_pools = {
            ('ethereum', 'polygon'): 1000000,
            ('ethereum', 'arbitrum'): 500000,
            ('polygon', 'arbitrum'): 300000,
            ('polygon', 'optimism'): 200000
        }

    def find_optimal_route(
        self,
        source: str,
        destination: str,
        amount: float
    ) -> Optional[PaymentRoute]:
        """
        Find optimal payment route

        Args:
            source: Source network
            destination: Destination network
            amount: Payment amount

        Returns:
            Optimal route or None
        """
        if source == destination:
            return PaymentRoute(
                path=[source],
                cost=0,
                estimated_time=0,
                liquidity_available=float('inf')
            )

        # Direct route
        direct_cost = self._calculate_route_cost(source, destination, amount)
        if direct_cost is not None:
            return PaymentRoute(
                path=[source, destination],
                cost=direct_cost,
                estimated_time=self._estimate_time([source, destination]),
                liquidity_available=self._get_liquidity(source, destination)
            )

        # Multi-hop routes
        best_route = None
        best_cost = float('inf')

        for intermediate in self.networks.keys():
            if intermediate != source and intermediate != destination:
                cost1 = self._calculate_route_cost(source, intermediate, amount)
                cost2 = self._calculate_route_cost(intermediate, destination, amount)

                if cost1 is not None and cost2 is not None:
                    total_cost = cost1 + cost2
                    if total_cost < best_cost:
                        best_cost = total_cost
                        best_route = PaymentRoute(
                            path=[source, intermediate, destination],
                            cost=total_cost,
                            estimated_time=self._estimate_time([source, intermediate, destination]),
                            liquidity_available=min(
                                self._get_liquidity(source, intermediate),
                                self._get_liquidity(intermediate, destination)
                            )
                        )

        return best_route

    def _calculate_route_cost(
        self,
        source: str,
        dest: str,
        amount: float
    ) -> Optional[float]:
        """
        Calculate cost for route segment

        Args:
            source: Source network
            dest: Destination network
            amount: Amount

        Returns:
            Cost or None if route not available
        """
        if source not in self.networks or dest not in self.networks:
            return None

        # Gas cost
        gas_price = self.networks[source]['gas_price']
        gas_cost = gas_price * 21000  # Base transaction

        # Slippage cost
        liquidity = self._get_liquidity(source, dest)
        if liquidity == 0:
            return None

        slippage = amount * (amount / (2 * liquidity))
        slippage_cost = amount * slippage

        # Time cost (opportunity cost)
        time = self.networks[source]['speed']
        time_cost = amount * 0.0001 * time  # 0.01% per second

        total_cost = gas_cost + slippage_cost + time_cost

        return total_cost

    def _get_liquidity(self, source: str, dest: str) -> float:
        """Get liquidity between networks"""
        key = (source, dest)
        reverse_key = (dest, source)

        if key in self.liquidity_pools:
            return self.liquidity_pools[key]
        elif reverse_key in self.liquidity_pools:
            return self.liquidity_pools[reverse_key]

        return 0

    def _estimate_time(self, path: List[str]) -> float:
        """Estimate time for path"""
        total_time = 0
        for network in path:
            if network in self.networks:
                total_time += self.networks[network]['speed']
        return total_time
