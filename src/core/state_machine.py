"""
Smart402 Master State Machine
Implements the core state transition logic for contract processing
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import time


class ContractState(Enum):
    """State space definition for contract processing"""
    IDLE = "s0"  # Initial state
    DISCOVERY = "s1"  # Contract Discovery (AEO)
    UNDERSTANDING = "s2"  # Contract Understanding (LLMO)
    COMPILATION = "s3"  # Smart Contract Compilation (SCC)
    VERIFICATION = "s4"  # Condition Verification (Oracle)
    EXECUTION = "s5"  # Payment Execution (X402)
    SETTLEMENT = "s6"  # Settlement Confirmation (Blockchain)
    COMPLETED = "s7"  # Contract Completion
    FAILED = "s_error"  # Error state


@dataclass
class StateTransition:
    """Represents a state transition with metadata"""
    from_state: ContractState
    to_state: ContractState
    condition: str
    timestamp: float
    probability: float
    metadata: Dict


class Smart402StateMachine:
    """
    Main algorithmic flow with state transitions

    State Space: S = {s₀, s₁, s₂, s₃, s₄, s₅, s₆, s₇}
    Transition Function: δ: S × Σ → S

    Implements probabilistic state transitions using softmax:
    P(s_next | s_current, condition) = exp(β * Q(s_current, condition, s_next)) /
                                        Σ exp(β * Q(s_current, condition, s'))
    """

    def __init__(self, beta: float = 1.0):
        """
        Initialize state machine

        Args:
            beta: Confidence parameter for transition probability
        """
        self.beta = beta
        self.current_state = ContractState.IDLE
        self.state_history: List[StateTransition] = []

        # Quality function Q(state, condition, next_state)
        self.Q: Dict[ContractState, Dict[str, Dict[ContractState, float]]] = {}
        self._initialize_quality_function()

        # Define allowed transitions
        self.allowed_transitions = {
            ContractState.IDLE: [ContractState.DISCOVERY],
            ContractState.DISCOVERY: [ContractState.UNDERSTANDING, ContractState.FAILED],
            ContractState.UNDERSTANDING: [ContractState.COMPILATION, ContractState.FAILED],
            ContractState.COMPILATION: [ContractState.VERIFICATION, ContractState.FAILED],
            ContractState.VERIFICATION: [ContractState.EXECUTION, ContractState.FAILED],
            ContractState.EXECUTION: [ContractState.SETTLEMENT, ContractState.FAILED],
            ContractState.SETTLEMENT: [ContractState.COMPLETED, ContractState.FAILED],
            ContractState.COMPLETED: [],
            ContractState.FAILED: []
        }

    def _initialize_quality_function(self):
        """Initialize quality function with default values"""
        states = list(ContractState)
        conditions = ["success", "failure", "timeout", "invalid"]

        for state in states:
            self.Q[state] = {}
            for condition in conditions:
                self.Q[state][condition] = {}
                for next_state in states:
                    # Default quality scores
                    self.Q[state][condition][next_state] = np.random.random()

    def softmax(self, values: np.ndarray) -> np.ndarray:
        """
        Softmax function for probability normalization

        Args:
            values: Array of quality scores

        Returns:
            Probability distribution
        """
        exp_values = np.exp(self.beta * values)
        return exp_values / np.sum(exp_values)

    def transition_probability(
        self,
        s_current: ContractState,
        s_next: ContractState,
        condition: str
    ) -> float:
        """
        Calculate transition probability using softmax

        P(s_next | s_current, condition) =
            exp(β * Q(s_current, condition, s_next)) /
            Σ exp(β * Q(s_current, condition, s'))

        Args:
            s_current: Current state
            s_next: Next state
            condition: Transition condition

        Returns:
            Probability of transition
        """
        if condition not in self.Q[s_current]:
            return 0.0

        allowed_next = self.allowed_transitions.get(s_current, [])
        if s_next not in allowed_next:
            return 0.0

        # Get quality scores for all possible next states
        qualities = np.array([
            self.Q[s_current][condition].get(state, 0.0)
            for state in allowed_next
        ])

        # Calculate probabilities
        probabilities = self.softmax(qualities)

        # Find index of s_next
        try:
            idx = allowed_next.index(s_next)
            return float(probabilities[idx])
        except ValueError:
            return 0.0

    def can_transition(self, to_state: ContractState) -> bool:
        """
        Check if transition to given state is allowed

        Args:
            to_state: Target state

        Returns:
            True if transition is allowed
        """
        allowed = self.allowed_transitions.get(self.current_state, [])
        return to_state in allowed

    def transition(
        self,
        to_state: ContractState,
        condition: str = "success",
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Execute state transition

        Args:
            to_state: Target state
            condition: Transition condition
            metadata: Additional transition metadata

        Returns:
            True if transition successful
        """
        if not self.can_transition(to_state):
            return False

        probability = self.transition_probability(
            self.current_state,
            to_state,
            condition
        )

        # Record transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            condition=condition,
            timestamp=time.time(),
            probability=probability,
            metadata=metadata or {}
        )

        self.state_history.append(transition)
        self.current_state = to_state

        return True

    def get_state_history(self) -> List[StateTransition]:
        """
        Get complete state transition history

        Returns:
            List of state transitions
        """
        return self.state_history.copy()

    def update_quality(
        self,
        state: ContractState,
        condition: str,
        next_state: ContractState,
        quality: float
    ):
        """
        Update quality function based on observed outcomes

        Args:
            state: Current state
            condition: Transition condition
            next_state: Next state
            quality: Observed quality score
        """
        if state not in self.Q:
            self.Q[state] = {}
        if condition not in self.Q[state]:
            self.Q[state][condition] = {}

        # Update using exponential moving average
        alpha = 0.1  # Learning rate
        old_quality = self.Q[state][condition].get(next_state, 0.0)
        self.Q[state][condition][next_state] = (
            alpha * quality + (1 - alpha) * old_quality
        )

    def reset(self):
        """Reset state machine to initial state"""
        self.current_state = ContractState.IDLE
        self.state_history = []

    def get_statistics(self) -> Dict:
        """
        Calculate statistics about state transitions

        Returns:
            Dictionary of statistics
        """
        if not self.state_history:
            return {
                "total_transitions": 0,
                "success_rate": 0.0,
                "average_probability": 0.0,
                "states_visited": []
            }

        total = len(self.state_history)
        successful = sum(
            1 for t in self.state_history
            if t.to_state != ContractState.FAILED
        )

        avg_prob = np.mean([t.probability for t in self.state_history])

        states_visited = list(set(
            t.to_state for t in self.state_history
        ))

        return {
            "total_transitions": total,
            "success_rate": successful / total if total > 0 else 0.0,
            "average_probability": float(avg_prob),
            "states_visited": [s.value for s in states_visited],
            "current_state": self.current_state.value
        }
