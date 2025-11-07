"""
Semantic Parsing for Contract Understanding
"""

import numpy as np
from typing import Dict, List, Tuple


class SemanticParser:
    """
    Parse contract semantics using dependency parsing

    Dependency score:
    D(w₁, w₂) = PMI(w₁, w₂) + dist_penalty(w₁, w₂)

    where:
    PMI(w₁, w₂) = log(P(w₁, w₂)/(P(w₁)P(w₂)))
    dist_penalty = -α * |pos(w₁) - pos(w₂)|
    """

    def __init__(self, alpha: float = 0.1):
        """
        Initialize semantic parser

        Args:
            alpha: Distance penalty coefficient
        """
        self.alpha = alpha
        self.word_frequencies: Dict[str, int] = {}
        self.bigram_frequencies: Dict[Tuple[str, str], int] = {}

    def parse_contract_semantics(self, contract_text: str) -> Dict:
        """
        Extract semantic structure from contract

        Args:
            contract_text: Raw contract text

        Returns:
            Semantic structure
        """
        # Tokenize
        words = contract_text.lower().split()

        # Build dependency tree
        tree = self._build_dependency_tree(words)

        # Extract components
        components = self._extract_components(tree, words)

        return {
            'tree': tree,
            'components': components,
            'word_count': len(words),
            'unique_words': len(set(words))
        }

    def _build_dependency_tree(self, words: List[str]) -> Dict:
        """
        Build dependency tree using maximum spanning tree

        Args:
            words: List of words

        Returns:
            Dependency tree structure
        """
        n = len(words)

        if n == 0:
            return {'root': None, 'dependencies': []}

        # Calculate scores matrix
        scores = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    scores[i][j] = self._dependency_score(
                        words[i], words[j], i, j
                    )

        # Find highest scoring dependencies (simplified MST)
        dependencies = []
        for i in range(1, n):
            best_head = 0
            best_score = scores[0][i]

            for j in range(n):
                if j != i and scores[j][i] > best_score:
                    best_head = j
                    best_score = scores[j][i]

            dependencies.append({
                'head': best_head,
                'dependent': i,
                'score': best_score
            })

        return {
            'root': 0,
            'dependencies': dependencies
        }

    def _dependency_score(
        self,
        word1: str,
        word2: str,
        pos1: int,
        pos2: int
    ) -> float:
        """
        Calculate dependency score between two words

        Args:
            word1: First word
            word2: Second word
            pos1: Position of first word
            pos2: Position of second word

        Returns:
            Dependency score
        """
        # PMI component
        pmi = self._calculate_pmi(word1, word2)

        # Distance penalty
        distance = abs(pos1 - pos2)
        penalty = -self.alpha * distance

        return pmi + penalty

    def _calculate_pmi(self, word1: str, word2: str) -> float:
        """
        Calculate Pointwise Mutual Information

        PMI(w₁, w₂) = log(P(w₁, w₂) / (P(w₁)P(w₂)))

        Args:
            word1: First word
            word2: Second word

        Returns:
            PMI score
        """
        # Get frequencies (with smoothing)
        freq1 = self.word_frequencies.get(word1, 1)
        freq2 = self.word_frequencies.get(word2, 1)
        bigram_freq = self.bigram_frequencies.get((word1, word2), 1)

        # Total words
        total = sum(self.word_frequencies.values()) + len(self.word_frequencies)

        # Probabilities
        p1 = freq1 / total
        p2 = freq2 / total
        p12 = bigram_freq / total

        # PMI
        pmi = np.log((p12 + 1e-10) / (p1 * p2 + 1e-10))

        return pmi

    def _extract_components(self, tree: Dict, words: List[str]) -> Dict:
        """
        Extract contract components from dependency tree

        Args:
            tree: Dependency tree
            words: List of words

        Returns:
            Extracted components
        """
        components = {
            'parties': [],
            'obligations': [],
            'conditions': [],
            'payments': [],
            'timelines': [],
            'smart_contract_triggers': []
        }

        # Pattern matching for different components
        party_keywords = ['party', 'parties', 'participant', 'entity']
        obligation_keywords = ['shall', 'must', 'required', 'obligated']
        condition_keywords = ['if', 'when', 'upon', 'provided']
        payment_keywords = ['payment', 'pay', 'amount', 'fee', 'price']

        for i, word in enumerate(words):
            if word in party_keywords:
                components['parties'].append({'word': word, 'position': i})
            elif word in obligation_keywords:
                components['obligations'].append({'word': word, 'position': i})
            elif word in condition_keywords:
                components['conditions'].append({'word': word, 'position': i})
            elif word in payment_keywords:
                components['payments'].append({'word': word, 'position': i})

        return components

    def update_frequencies(self, text: str):
        """
        Update word and bigram frequencies

        Args:
            text: Training text
        """
        words = text.lower().split()

        # Update word frequencies
        for word in words:
            self.word_frequencies[word] = self.word_frequencies.get(word, 0) + 1

        # Update bigram frequencies
        for i in range(len(words) - 1):
            bigram = (words[i], words[i + 1])
            self.bigram_frequencies[bigram] = self.bigram_frequencies.get(bigram, 0) + 1
