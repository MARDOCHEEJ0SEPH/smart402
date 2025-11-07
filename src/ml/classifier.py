"""
Contract Classifier using simple ML
"""

import numpy as np
from typing import Dict, List


class ContractClassifier:
    """
    Multi-class contract classification

    Categories:
    - Payment contract
    - Service contract
    - Smart contract executable
    - Escrow contract
    - Multi-party agreement
    """

    def __init__(self):
        """Initialize classifier"""
        self.categories = [
            'payment',
            'service',
            'smart_executable',
            'escrow',
            'multi_party'
        ]
        self.feature_weights = np.random.random(10)

    def classify(self, contract: Dict) -> str:
        """
        Classify contract

        Args:
            contract: Contract data

        Returns:
            Contract category
        """
        # Extract features
        features = self._extract_features(contract)

        # Calculate scores
        scores = []
        for category in self.categories:
            score = self._calculate_score(features, category)
            scores.append(score)

        # Return highest scoring category
        best_idx = np.argmax(scores)
        return self.categories[best_idx]

    def _extract_features(self, contract: Dict) -> np.ndarray:
        """Extract features from contract"""
        features = np.zeros(10)

        # Feature 0: Has amount
        features[0] = 1.0 if contract.get('amount', 0) > 0 else 0.0

        # Feature 1: Number of parties
        features[1] = len(contract.get('parties', [])) / 10.0

        # Feature 2: Has smart contract
        features[2] = 1.0 if contract.get('smart_contract_code') else 0.0

        # Feature 3: Has conditions
        features[3] = len(contract.get('conditions', [])) / 5.0

        # Feature 4: Text length
        text = str(contract.get('terms', ''))
        features[4] = len(text) / 1000.0

        return features

    def _calculate_score(self, features: np.ndarray, category: str) -> float:
        """Calculate score for category"""
        # Simple weighted sum
        score = np.dot(features, self.feature_weights)

        # Category-specific adjustments
        if category == 'payment' and features[0] > 0:
            score += 0.5
        elif category == 'smart_executable' and features[2] > 0:
            score += 0.5
        elif category == 'multi_party' and features[1] > 0.2:
            score += 0.3

        return score
