"""
LLMO Engine
Main orchestration for Large Language Model Optimization
"""

from typing import Dict, List, Optional
from .understanding import UnderstandingScorer
from .parser import SemanticParser
from .encoder import ContractEncoder


class LLMOEngine:
    """
    Main LLMO Engine integrating all components
    """

    def __init__(self):
        """Initialize LLMO engine"""
        self.scorer = UnderstandingScorer()
        self.parser = SemanticParser()
        self.encoder = ContractEncoder()

    async def optimize_understanding(
        self,
        contracts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Optimize contracts for LLM understanding

        Args:
            contracts: List of contracts to process

        Returns:
            Contracts with understanding optimization
        """
        if contracts is None:
            contracts = []

        understood = []

        for contract in contracts:
            # Calculate understanding score
            understanding_score = self.scorer.calculate_llmo_score(contract)

            # Parse semantics
            contract_text = self._extract_text(contract)
            semantic_structure = self.parser.parse_contract_semantics(contract_text)

            # Encode for LLM
            encoding = self.encoder.encode_contract_for_llm(contract)

            # Add to contract
            contract['understanding_score'] = understanding_score
            contract['semantic_structure'] = semantic_structure
            contract['llm_encoding'] = encoding
            contract['llm_optimized'] = True

            understood.append(contract)

            # Update parser with this contract
            self.parser.update_frequencies(contract_text)

        return understood

    def _extract_text(self, contract: Dict) -> str:
        """
        Extract text from contract

        Args:
            contract: Contract data

        Returns:
            Contract text
        """
        parts = []

        for key in ['description', 'terms', 'conditions']:
            if key in contract:
                value = contract[key]
                if isinstance(value, str):
                    parts.append(value)
                elif isinstance(value, list):
                    parts.extend(str(v) for v in value)

        return ' '.join(parts)
