"""
Tests for core state machine and orchestration
"""

import pytest
from src.core.state_machine import Smart402StateMachine, ContractState
from src.core.optimization import MasterOptimizationFunction, ContractMetrics
from src.core.orchestrator import Smart402Orchestrator


class TestStateMachine:
    """Test state machine functionality"""

    def test_initialization(self):
        """Test state machine initialization"""
        sm = Smart402StateMachine()
        assert sm.current_state == ContractState.IDLE
        assert len(sm.state_history) == 0

    def test_valid_transition(self):
        """Test valid state transition"""
        sm = Smart402StateMachine()
        success = sm.transition(ContractState.DISCOVERY)
        assert success
        assert sm.current_state == ContractState.DISCOVERY

    def test_invalid_transition(self):
        """Test invalid state transition"""
        sm = Smart402StateMachine()
        success = sm.transition(ContractState.COMPLETED)
        assert not success
        assert sm.current_state == ContractState.IDLE

    def test_transition_history(self):
        """Test transition history tracking"""
        sm = Smart402StateMachine()
        sm.transition(ContractState.DISCOVERY)
        sm.transition(ContractState.UNDERSTANDING)

        history = sm.get_state_history()
        assert len(history) == 2
        assert history[0].to_state == ContractState.DISCOVERY
        assert history[1].to_state == ContractState.UNDERSTANDING


class TestOptimization:
    """Test optimization function"""

    def test_objective_calculation(self):
        """Test objective function calculation"""
        opt = MasterOptimizationFunction()
        metrics = ContractMetrics(
            value=0.8,
            discoverability=0.7,
            understanding=0.9,
            compilation_score=0.85,
            execution_efficiency=0.75,
            risk=0.2
        )

        objective = opt.calculate_objective(metrics)
        assert 0 <= objective <= 1.5

    def test_risk_calculation(self):
        """Test risk function"""
        opt = MasterOptimizationFunction()
        contract = {
            'complexity': 0.5,
            'counterparty_risk': 0.3,
            'execution_risk': 0.2,
            'security_risk': 0.1
        }

        risk = opt.calculate_risk_function(contract)
        assert 0 <= risk <= 1


class TestOrchestrator:
    """Test orchestrator"""

    @pytest.mark.asyncio
    async def test_discovery_phase(self):
        """Test discovery phase"""
        orchestrator = Smart402Orchestrator()
        discovered = await orchestrator._discovery_phase()
        assert isinstance(discovered, list)

    def test_initialization(self):
        """Test orchestrator initialization"""
        orchestrator = Smart402Orchestrator()
        assert orchestrator.state_machine is not None
        assert orchestrator.optimizer is not None
