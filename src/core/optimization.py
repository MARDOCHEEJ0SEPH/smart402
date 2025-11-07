"""
Master Optimization Function for Smart402

Implements the objective function:
maximize F(C) = α₁·V(C) + α₂·D(C) + α₃·U(C) + α₄·S(C) + α₅·E(C) - γ·R(C)

where:
- C = Contract instance
- V(C) = Value function (economic value)
- D(C) = Discoverability score (AEO)
- U(C) = Understanding score (LLMO)
- S(C) = Smart contract compilation score (SCC)
- E(C) = Execution efficiency (X402)
- R(C) = Risk function
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ContractMetrics:
    """Metrics for a contract instance"""
    value: float = 0.0
    discoverability: float = 0.0
    understanding: float = 0.0
    compilation_score: float = 0.0
    execution_efficiency: float = 0.0
    risk: float = 0.0


@dataclass
class OptimizationConstraints:
    """Constraints for optimization"""
    min_legal_compliance: float = 0.8
    max_gas_cost: float = 1000000
    contract_must_be_valid: bool = True
    max_time: float = 300.0  # seconds


class MasterOptimizationFunction:
    """
    Master optimization function for Smart402 system

    Objective Function:
    maximize F(C) = α₁·V(C) + α₂·D(C) + α₃·U(C) + α₄·S(C) + α₅·E(C) - γ·R(C)

    Subject to constraints:
    - Legal compliance: L(C) ≥ L_min
    - Gas efficiency: G(C) ≤ G_max
    - Contract validity: V(C) = Valid ∧ Verifiable
    - Time bounds: T(C) ≤ T_max
    """

    def __init__(
        self,
        alpha1: float = 0.3,  # Value weight
        alpha2: float = 0.15,  # Discoverability weight
        alpha3: float = 0.2,  # Understanding weight
        alpha4: float = 0.15,  # Compilation weight
        alpha5: float = 0.2,  # Execution weight
        gamma: float = 0.5  # Risk aversion parameter
    ):
        """
        Initialize optimization function

        Args:
            alpha1-5: Weight parameters for different objectives
            gamma: Risk aversion parameter
        """
        # Normalize weights
        total_alpha = alpha1 + alpha2 + alpha3 + alpha4 + alpha5
        self.alpha1 = alpha1 / total_alpha
        self.alpha2 = alpha2 / total_alpha
        self.alpha3 = alpha3 / total_alpha
        self.alpha4 = alpha4 / total_alpha
        self.alpha5 = alpha5 / total_alpha
        self.gamma = gamma

    def calculate_objective(
        self,
        metrics: ContractMetrics,
        constraints: Optional[OptimizationConstraints] = None
    ) -> float:
        """
        Calculate objective function value

        F(C) = α₁·V(C) + α₂·D(C) + α₃·U(C) + α₄·S(C) + α₅·E(C) - γ·R(C)

        Args:
            metrics: Contract metrics
            constraints: Optional constraints

        Returns:
            Objective value
        """
        objective = (
            self.alpha1 * metrics.value +
            self.alpha2 * metrics.discoverability +
            self.alpha3 * metrics.understanding +
            self.alpha4 * metrics.compilation_score +
            self.alpha5 * metrics.execution_efficiency -
            self.gamma * metrics.risk
        )

        return objective

    def check_constraints(
        self,
        metrics: ContractMetrics,
        constraints: OptimizationConstraints,
        legal_compliance: float,
        gas_cost: float,
        is_valid: bool,
        execution_time: float
    ) -> bool:
        """
        Check if all constraints are satisfied

        Args:
            metrics: Contract metrics
            constraints: Constraint thresholds
            legal_compliance: Legal compliance score [0,1]
            gas_cost: Estimated gas cost
            is_valid: Whether contract is valid
            execution_time: Execution time in seconds

        Returns:
            True if all constraints satisfied
        """
        if legal_compliance < constraints.min_legal_compliance:
            return False

        if gas_cost > constraints.max_gas_cost:
            return False

        if constraints.contract_must_be_valid and not is_valid:
            return False

        if execution_time > constraints.max_time:
            return False

        return True

    def optimize(
        self,
        candidates: list,
        constraints: Optional[OptimizationConstraints] = None
    ) -> Optional[Dict]:
        """
        Find optimal contract from candidates

        Args:
            candidates: List of contract candidates with metrics
            constraints: Optional constraints

        Returns:
            Optimal contract or None
        """
        if not candidates:
            return None

        if constraints is None:
            constraints = OptimizationConstraints()

        best_contract = None
        best_objective = -np.inf

        for candidate in candidates:
            metrics = candidate.get('metrics')
            if not metrics:
                continue

            # Check constraints
            if not self.check_constraints(
                metrics,
                constraints,
                candidate.get('legal_compliance', 1.0),
                candidate.get('gas_cost', 0),
                candidate.get('is_valid', True),
                candidate.get('execution_time', 0)
            ):
                continue

            # Calculate objective
            objective = self.calculate_objective(metrics, constraints)

            if objective > best_objective:
                best_objective = objective
                best_contract = candidate

        return best_contract

    def calculate_value_function(self, contract: Dict) -> float:
        """
        Calculate economic value V(C)

        Args:
            contract: Contract data

        Returns:
            Value score [0,1]
        """
        # Economic value based on payment amount, parties, etc.
        amount = contract.get('amount', 0)
        parties = len(contract.get('parties', []))

        # Normalize value (log scale for large amounts)
        value = np.log(1 + amount) / 20  # Normalize to roughly [0,1]
        value += parties * 0.1  # Bonus for multi-party

        return min(value, 1.0)

    def calculate_risk_function(self, contract: Dict) -> float:
        """
        Calculate risk function R(C)

        Risk factors:
        - Complexity risk
        - Counterparty risk
        - Execution risk
        - Smart contract security risk

        Args:
            contract: Contract data

        Returns:
            Risk score [0,1]
        """
        complexity = contract.get('complexity', 0.5)
        counterparty_risk = contract.get('counterparty_risk', 0.3)
        execution_risk = contract.get('execution_risk', 0.2)
        security_risk = contract.get('security_risk', 0.1)

        # Weighted risk
        risk = (
            0.3 * complexity +
            0.3 * counterparty_risk +
            0.2 * execution_risk +
            0.2 * security_risk
        )

        return min(risk, 1.0)

    def gradient(self, metrics: ContractMetrics) -> Dict[str, float]:
        """
        Calculate gradient of objective function

        ∇F = [∂F/∂V, ∂F/∂D, ∂F/∂U, ∂F/∂S, ∂F/∂E, ∂F/∂R]

        Args:
            metrics: Current contract metrics

        Returns:
            Gradient dictionary
        """
        return {
            'value': self.alpha1,
            'discoverability': self.alpha2,
            'understanding': self.alpha3,
            'compilation': self.alpha4,
            'execution': self.alpha5,
            'risk': -self.gamma
        }
