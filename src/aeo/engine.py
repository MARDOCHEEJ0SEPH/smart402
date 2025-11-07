"""
AEO Engine
Main orchestration for Answer Engine Optimization
"""

from typing import Dict, List, Optional
from .scoring import AEOScorer
from .content_generator import ContentGenerator
from .semantic_graph import SemanticGraphBuilder


class AEOEngine:
    """
    Main AEO Engine integrating all components
    """

    def __init__(self):
        """Initialize AEO engine"""
        self.scorer = AEOScorer()
        self.content_generator = ContentGenerator()
        self.graph_builder = SemanticGraphBuilder()
        self.optimized_contracts: Dict[str, Dict] = {}

    async def optimize_discovery(
        self,
        contracts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Optimize contracts for AI discovery

        Args:
            contracts: Optional list of contracts to optimize

        Returns:
            Optimized contracts
        """
        if contracts is None:
            contracts = []

        optimized = []

        for contract in contracts:
            # Calculate AEO score
            aeo_score = self.scorer.calculate_aeo_score(contract)

            # Generate optimized content
            target_query = contract.get('target_query', contract.get('type', ''))
            optimized_content = self.content_generator.generate_aeo_content(
                contract,
                target_query
            )

            # Add to contract
            contract['aeo_score'] = aeo_score
            contract['optimized_content'] = optimized_content
            contract['optimized'] = True

            optimized.append(contract)

            # Store
            contract_id = contract.get('id', 'unknown')
            self.optimized_contracts[contract_id] = contract

        # Build semantic graph if multiple contracts
        if len(optimized) > 1:
            graph = self.graph_builder.build_semantic_graph(optimized)

            # Add graph information to contracts
            for contract in optimized:
                contract_id = contract.get('id')
                if contract_id:
                    contract['cluster'] = graph['clusters'].get(contract_id, 0)
                    contract['related'] = self.graph_builder.get_related_contracts(
                        contract_id
                    )

        return optimized

    def get_optimization_report(self, contract_id: str) -> Optional[Dict]:
        """
        Get detailed optimization report for a contract

        Args:
            contract_id: Contract identifier

        Returns:
            Optimization report
        """
        if contract_id not in self.optimized_contracts:
            return None

        contract = self.optimized_contracts[contract_id]

        return {
            'contract_id': contract_id,
            'aeo_score': contract.get('aeo_score', 0.0),
            'content_length': len(contract.get('optimized_content', '')),
            'cluster': contract.get('cluster'),
            'related_contracts': contract.get('related', []),
            'optimization_timestamp': contract.get('optimized_at')
        }
