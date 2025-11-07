"""
Byzantine Consensus Algorithm (PBFT)

Safety: All honest nodes agree on same value
Liveness: Protocol terminates with probability 1
Requirement: n ≥ 3f + 1
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import time


@dataclass
class ConsensusMessage:
    """Consensus message"""
    msg_type: str  # pre-prepare, prepare, commit
    view: int
    sequence: int
    digest: str
    node_id: str
    timestamp: float


class ByzantineConsensus:
    """
    Practical Byzantine Fault Tolerance (PBFT) implementation

    Phases:
    1. Pre-prepare: Leader broadcasts
    2. Prepare: Nodes echo
    3. Commit: Nodes confirm

    Requirement: n ≥ 3f + 1
    """

    def __init__(self, node_id: str, num_nodes: int = 7):
        """
        Initialize Byzantine consensus

        Args:
            node_id: This node's identifier
            num_nodes: Total number of nodes
        """
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.f = (num_nodes - 1) // 3  # Max faulty nodes
        self.view = 0
        self.sequence = 0
        self.messages: List[ConsensusMessage] = []

    def is_valid_config(self) -> bool:
        """Check if configuration is valid for PBFT"""
        return self.num_nodes >= 3 * self.f + 1

    def run_consensus(self, value: Dict) -> Dict:
        """
        Run consensus protocol

        Args:
            value: Value to reach consensus on

        Returns:
            Consensus result
        """
        if not self.is_valid_config():
            return {
                'success': False,
                'reason': 'invalid_configuration'
            }

        # Phase 1: Pre-prepare
        pre_prepare_votes = self._pre_prepare_phase(value)

        if not self._has_supermajority(pre_prepare_votes):
            return {
                'success': False,
                'reason': 'insufficient_pre_prepare_votes',
                'votes': len(pre_prepare_votes)
            }

        # Phase 2: Prepare
        prepare_votes = self._prepare_phase(value)

        if not self._has_supermajority(prepare_votes):
            return {
                'success': False,
                'reason': 'insufficient_prepare_votes',
                'votes': len(prepare_votes)
            }

        # Phase 3: Commit
        commit_votes = self._commit_phase(value)

        if not self._has_supermajority(commit_votes):
            return {
                'success': False,
                'reason': 'insufficient_commit_votes',
                'votes': len(commit_votes)
            }

        return {
            'success': True,
            'value': value,
            'consensus_votes': len(commit_votes),
            'timestamp': time.time()
        }

    def _pre_prepare_phase(self, value: Dict) -> List[ConsensusMessage]:
        """
        Pre-prepare phase

        Args:
            value: Value to prepare

        Returns:
            List of pre-prepare votes
        """
        votes = []

        # Simulate voting (in practice, would send messages)
        for i in range(self.num_nodes):
            if i < self.num_nodes - self.f:  # Honest nodes
                msg = ConsensusMessage(
                    msg_type='pre-prepare',
                    view=self.view,
                    sequence=self.sequence,
                    digest=str(hash(str(value))),
                    node_id=f'node_{i}',
                    timestamp=time.time()
                )
                votes.append(msg)
                self.messages.append(msg)

        return votes

    def _prepare_phase(self, value: Dict) -> List[ConsensusMessage]:
        """Prepare phase"""
        votes = []

        for i in range(self.num_nodes):
            if i < self.num_nodes - self.f:
                msg = ConsensusMessage(
                    msg_type='prepare',
                    view=self.view,
                    sequence=self.sequence,
                    digest=str(hash(str(value))),
                    node_id=f'node_{i}',
                    timestamp=time.time()
                )
                votes.append(msg)
                self.messages.append(msg)

        return votes

    def _commit_phase(self, value: Dict) -> List[ConsensusMessage]:
        """Commit phase"""
        votes = []

        for i in range(self.num_nodes):
            if i < self.num_nodes - self.f:
                msg = ConsensusMessage(
                    msg_type='commit',
                    view=self.view,
                    sequence=self.sequence,
                    digest=str(hash(str(value))),
                    node_id=f'node_{i}',
                    timestamp=time.time()
                )
                votes.append(msg)
                self.messages.append(msg)

        return votes

    def _has_supermajority(self, votes: List[ConsensusMessage]) -> bool:
        """
        Check if supermajority exists

        Supermajority: > 2f votes
        """
        required = 2 * self.f + 1
        return len(votes) >= required
