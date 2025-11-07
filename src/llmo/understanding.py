"""
Contract Understanding Score Algorithm

Measures how well an LLM understands the contract:
U(C, M) = Σᵢ πᵢ * P(correct_interpretation | clauseᵢ, M)
"""

import numpy as np
from typing import Dict, List


class UnderstandingScorer:
    """
    Calculate LLMO understanding scores

    U(C, M) = Σᵢ πᵢ * P(correct_interpretation | clauseᵢ, M)

    where:
    - C = contract
    - M = LLM model
    - πᵢ = importance weight of clause i
    - P = probability of correct interpretation
    """

    def __init__(self):
        """Initialize understanding scorer"""
        self.model_scores: Dict[str, List[float]] = {}

    def calculate_llmo_score(self, contract: Dict, llm_model: str = "default") -> float:
        """
        Calculate overall LLMO understanding score

        Args:
            contract: Contract data
            llm_model: LLM model identifier

        Returns:
            Understanding score [0, 1]
        """
        # Extract clauses
        clauses = self._extract_clauses(contract)

        if not clauses:
            return 0.0

        # Calculate scores for each clause
        total_score = 0.0
        total_weight = 0.0

        for clause in clauses:
            importance = clause.get('importance', 1.0)
            comprehension = self.comprehension_probability(
                clause.get('text', ''),
                llm_model
            )

            total_score += importance * comprehension
            total_weight += importance

        # Normalize
        understanding_score = total_score / total_weight if total_weight > 0 else 0.0

        return understanding_score

    def comprehension_probability(self, text: str, model: str) -> float:
        """
        Calculate comprehension probability using perplexity

        Perplexity = exp(H(p))
        where H(p) = -Σ p(x) log p(x)

        Comprehension = 1 / (1 + perplexity/100)

        Args:
            text: Text to analyze
            model: Model identifier

        Returns:
            Comprehension probability [0, 1]
        """
        if not text:
            return 0.0

        # Calculate perplexity (simplified)
        tokens = text.split()
        n_tokens = len(tokens)

        if n_tokens == 0:
            return 0.0

        # Simulate perplexity based on text complexity
        perplexity = self._estimate_perplexity(tokens)

        # Convert to comprehension score
        comprehension = 1 / (1 + perplexity / 100)

        return comprehension

    def _estimate_perplexity(self, tokens: List[str]) -> float:
        """
        Estimate perplexity from tokens
        (Simplified - would use actual LLM)

        Args:
            tokens: List of tokens

        Returns:
            Perplexity score
        """
        # Factors affecting perplexity
        n_tokens = len(tokens)

        # Vocabulary diversity
        unique_tokens = len(set(tokens))
        diversity = unique_tokens / n_tokens if n_tokens > 0 else 0

        # Average token length (complexity indicator)
        avg_length = np.mean([len(t) for t in tokens]) if tokens else 0

        # Estimate perplexity
        # Lower diversity and longer tokens = higher perplexity
        perplexity = 50 * (1 / (diversity + 0.1)) * (avg_length / 5)

        return max(perplexity, 1.0)

    def ensemble_understanding(self, contract: Dict) -> float:
        """
        Multi-model ensemble understanding

        Args:
            contract: Contract data

        Returns:
            Ensemble understanding score
        """
        models = ['gpt4', 'claude', 'llama', 'mistral']
        weights = [0.3, 0.3, 0.2, 0.2]

        scores = []
        for model in models:
            score = self.calculate_llmo_score(contract, model)
            scores.append(score)

        # Weighted average
        ensemble_score = np.average(scores, weights=weights)

        return ensemble_score

    def _extract_clauses(self, contract: Dict) -> List[Dict]:
        """
        Extract clauses from contract

        Args:
            contract: Contract data

        Returns:
            List of clause dictionaries
        """
        clauses = []

        # Extract from various fields
        if 'terms' in contract:
            terms = contract['terms']
            if isinstance(terms, str):
                # Split by sentences (simplified)
                sentences = terms.split('.')
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        clauses.append({
                            'id': f'clause_{i}',
                            'text': sentence.strip(),
                            'importance': 1.0,
                            'type': 'term'
                        })

        # Add specific clauses
        if 'obligations' in contract:
            for i, obligation in enumerate(contract['obligations']):
                clauses.append({
                    'id': f'obligation_{i}',
                    'text': str(obligation),
                    'importance': 1.5,  # Higher importance
                    'type': 'obligation'
                })

        if 'conditions' in contract:
            for i, condition in enumerate(contract['conditions']):
                clauses.append({
                    'id': f'condition_{i}',
                    'text': str(condition),
                    'importance': 1.3,
                    'type': 'condition'
                })

        return clauses
