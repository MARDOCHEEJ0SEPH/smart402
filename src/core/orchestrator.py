"""
Smart402 Orchestrator
Master orchestration algorithm integrating all components
"""

import asyncio
import time
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass

from .state_machine import Smart402StateMachine, ContractState
from .optimization import MasterOptimizationFunction, ContractMetrics


@dataclass
class PerformanceMetrics:
    """Performance metrics for the system"""
    discovery_rate: float = 0.0
    understanding_rate: float = 0.0
    compilation_rate: float = 0.0
    verification_rate: float = 0.0
    execution_rate: float = 0.0
    smart_contract_success_rate: float = 0.0
    total_value: float = 0.0
    average_time: float = 0.0
    error_rate: float = 0.0
    overall_efficiency: float = 0.0


class Smart402Orchestrator:
    """
    Master orchestration algorithm integrating all components

    Main optimization problem:
    maximize Σᵢ Σⱼ Σₖ Σₗ Value(AEO_i, LLMO_j, SCC_k, X402_l)

    subject to:
    - Legal_compliance(i,j,k,l) = True
    - SmartContract_validity(k) = True
    - Risk(i,j,k,l) < Risk_threshold
    - Performance(i,j,k,l) > Min_performance
    """

    def __init__(self):
        """Initialize orchestrator with all components"""
        self.state_machine = Smart402StateMachine()
        self.optimizer = MasterOptimizationFunction()
        self.contract_registry: Dict[str, Dict] = {}
        self.best_fitness = -np.inf
        self.current_configuration = self._default_configuration()
        self.best_configuration = self.current_configuration.copy()
        self.total_contracts = 0

    def _default_configuration(self) -> Dict:
        """Get default system configuration"""
        return {
            'aeo_weight': 0.15,
            'llmo_weight': 0.20,
            'scc_weight': 0.15,
            'x402_weight': 0.20,
            'value_weight': 0.30,
            'risk_aversion': 0.5,
            'parallel_processing': True,
            'cache_enabled': True,
            'optimization_iterations': 100
        }

    async def run(self, duration: Optional[float] = None):
        """
        Main orchestration loop

        Args:
            duration: Optional runtime duration in seconds
        """
        start_time = time.time()

        while True:
            # Check duration limit
            if duration and (time.time() - start_time) > duration:
                break

            try:
                # Step 1: Discovery phase (AEO)
                contracts_discovered = await self._discovery_phase()

                # Step 2: Understanding phase (LLMO)
                contracts_understood = await self._understanding_phase(
                    contracts_discovered
                )

                # Step 3: Compilation phase (SCC)
                contracts_compiled = await self._compilation_phase(
                    contracts_understood
                )

                # Step 4: Verification phase
                contracts_verified = await self._verification_phase(
                    contracts_compiled
                )

                # Step 5: Execution phase (X402)
                contracts_executed = await self._execution_phase(
                    contracts_verified
                )

                # Step 6: Calculate metrics
                metrics = self.calculate_metrics(
                    contracts_discovered,
                    contracts_understood,
                    contracts_compiled,
                    contracts_verified,
                    contracts_executed
                )

                # Step 7: Evolve system
                self.evolve_system(metrics)

                # Small delay before next iteration
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Orchestration error: {e}")
                await asyncio.sleep(5)

    async def _discovery_phase(self) -> List[Dict]:
        """
        Discovery phase using AEO

        Returns:
            List of discovered contracts
        """
        # Transition to discovery state
        self.state_machine.transition(ContractState.DISCOVERY)

        # Simulate discovery (would integrate with actual AEO engine)
        await asyncio.sleep(0.1)

        discovered = [
            {
                'id': f'contract_{i}',
                'type': 'payment',
                'amount': np.random.randint(100, 10000),
                'parties': ['party_a', 'party_b'],
                'discovered_at': time.time()
            }
            for i in range(np.random.randint(1, 5))
        ]

        return discovered

    async def _understanding_phase(self, contracts: List[Dict]) -> List[Dict]:
        """
        Understanding phase using LLMO

        Args:
            contracts: Discovered contracts

        Returns:
            Understood contracts
        """
        if not contracts:
            return []

        # Transition to understanding state
        self.state_machine.transition(ContractState.UNDERSTANDING)

        understood = []
        for contract in contracts:
            # Simulate understanding
            contract['understood'] = True
            contract['understanding_score'] = np.random.uniform(0.7, 1.0)
            contract['semantic_structure'] = {
                'parties': contract.get('parties', []),
                'obligations': [],
                'conditions': [],
                'payment': contract.get('amount', 0)
            }
            understood.append(contract)

        await asyncio.sleep(0.1)
        return understood

    async def _compilation_phase(self, contracts: List[Dict]) -> List[Dict]:
        """
        Compilation phase using SCC

        Args:
            contracts: Understood contracts

        Returns:
            Compiled contracts
        """
        if not contracts:
            return []

        # Transition to compilation state
        self.state_machine.transition(ContractState.COMPILATION)

        compiled = []
        for contract in contracts:
            # Simulate compilation
            if np.random.random() > 0.1:  # 90% success rate
                contract['compiled'] = True
                contract['smart_contract_code'] = f"contract_{contract['id']}"
                contract['gas_estimate'] = np.random.randint(50000, 200000)
                compiled.append(contract)

        await asyncio.sleep(0.1)
        return compiled

    async def _verification_phase(self, contracts: List[Dict]) -> List[Dict]:
        """
        Verification phase

        Args:
            contracts: Compiled contracts

        Returns:
            Verified contracts
        """
        if not contracts:
            return []

        # Transition to verification state
        self.state_machine.transition(ContractState.VERIFICATION)

        verified = []
        for contract in contracts:
            # Simulate verification
            if np.random.random() > 0.05:  # 95% pass rate
                contract['verified'] = True
                contract['security_score'] = np.random.uniform(0.8, 1.0)
                verified.append(contract)

        await asyncio.sleep(0.1)
        return verified

    async def _execution_phase(self, contracts: List[Dict]) -> List[Dict]:
        """
        Execution phase using X402

        Args:
            contracts: Verified contracts

        Returns:
            Executed contracts
        """
        if not contracts:
            return []

        # Transition to execution state
        self.state_machine.transition(ContractState.EXECUTION)

        executed = []
        for contract in contracts:
            # Simulate execution
            if np.random.random() > 0.02:  # 98% execution success
                contract['executed'] = True
                contract['execution_time'] = np.random.uniform(0.1, 2.0)
                contract['uses_smart_contract'] = 'smart_contract_code' in contract
                contract['value'] = contract.get('amount', 0)
                executed.append(contract)

                # Register contract
                self.contract_registry[contract['id']] = contract

        # Transition to settlement
        self.state_machine.transition(ContractState.SETTLEMENT)

        await asyncio.sleep(0.1)
        return executed

    def calculate_metrics(
        self,
        discovered: List[Dict],
        understood: List[Dict],
        compiled: List[Dict],
        verified: List[Dict],
        executed: List[Dict]
    ) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics

        Args:
            discovered: Discovered contracts
            understood: Understood contracts
            compiled: Compiled contracts
            verified: Verified contracts
            executed: Executed contracts

        Returns:
            Performance metrics
        """
        n_discovered = len(discovered)
        n_understood = len(understood)
        n_compiled = len(compiled)
        n_verified = len(verified)
        n_executed = len(executed)

        metrics = PerformanceMetrics()

        if n_discovered > 0:
            self.total_contracts += n_discovered
            metrics.discovery_rate = n_discovered / max(self.total_contracts, 1)
            metrics.understanding_rate = n_understood / n_discovered
        else:
            metrics.understanding_rate = 0.0

        if n_understood > 0:
            metrics.compilation_rate = n_compiled / n_understood

        if n_compiled > 0:
            metrics.verification_rate = n_verified / n_compiled

        if n_verified > 0:
            metrics.execution_rate = n_executed / n_verified

        if executed:
            metrics.total_value = sum(c.get('value', 0) for c in executed)
            metrics.average_time = np.mean([
                c.get('execution_time', 0) for c in executed
            ])
            sc_count = sum(1 for c in executed if c.get('uses_smart_contract'))
            metrics.smart_contract_success_rate = sc_count / len(executed)

        # Calculate overall efficiency (geometric mean)
        rates = [
            metrics.discovery_rate,
            metrics.understanding_rate,
            metrics.compilation_rate,
            metrics.verification_rate,
            metrics.execution_rate
        ]

        non_zero_rates = [r for r in rates if r > 0]
        if non_zero_rates:
            metrics.overall_efficiency = np.prod(non_zero_rates) ** (1 / len(non_zero_rates))

        return metrics

    def evolve_system(self, metrics: PerformanceMetrics) -> float:
        """
        Genetic algorithm for system evolution

        Fitness = α*efficiency + β*value - γ*errors + δ*sc_success_rate

        Args:
            metrics: Current performance metrics

        Returns:
            Fitness score
        """
        fitness = (
            0.25 * metrics.overall_efficiency +
            0.4 * np.log(metrics.total_value + 1) / 10 -
            0.15 * metrics.error_rate +
            0.2 * metrics.smart_contract_success_rate
        )

        if fitness > self.best_fitness:
            self.best_fitness = fitness
            self.best_configuration = self.current_configuration.copy()
        else:
            # Mutate configuration
            self._mutate_configuration()

        return fitness

    def _mutate_configuration(self):
        """Apply Gaussian mutation to configuration"""
        for key in self.current_configuration:
            if isinstance(self.current_configuration[key], (int, float)):
                mutation = np.random.normal(0, 0.1)
                self.current_configuration[key] += mutation
                # Ensure bounds
                self.current_configuration[key] = np.clip(
                    self.current_configuration[key],
                    0.0,
                    1.0
                )

    def get_statistics(self) -> Dict:
        """
        Get system statistics

        Returns:
            Dictionary of statistics
        """
        return {
            'state_machine': self.state_machine.get_statistics(),
            'total_contracts': self.total_contracts,
            'registry_size': len(self.contract_registry),
            'best_fitness': self.best_fitness,
            'current_configuration': self.current_configuration
        }
