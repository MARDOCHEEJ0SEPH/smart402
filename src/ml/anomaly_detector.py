"""
Anomaly Detection for Contracts
"""

import numpy as np
from typing import Dict, List


class AnomalyDetector:
    """
    Detect anomalous contracts using Isolation Forest-like algorithm

    Anomaly score:
    s(x, n) = 2^(-E(h(x))/c(n))

    where:
    - E(h(x)) = expected path length for x
    - c(n) = average path length
    """

    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector

        Args:
            contamination: Expected proportion of anomalies
        """
        self.contamination = contamination
        self.threshold = 0.6
        self.feature_stats: Dict = {}

    def fit(self, contracts: List[Dict]):
        """
        Fit detector on normal contracts

        Args:
            contracts: Training contracts
        """
        # Calculate feature statistics
        features_list = [self._extract_features(c) for c in contracts]

        if features_list:
            features_array = np.array(features_list)
            self.feature_stats = {
                'mean': np.mean(features_array, axis=0),
                'std': np.std(features_array, axis=0)
            }

    def detect(self, contract: Dict) -> bool:
        """
        Detect if contract is anomalous

        Args:
            contract: Contract to check

        Returns:
            True if anomalous
        """
        score = self.anomaly_score(contract)
        return score > self.threshold

    def anomaly_score(self, contract: Dict) -> float:
        """
        Calculate anomaly score

        Args:
            contract: Contract data

        Returns:
            Anomaly score [0, 1]
        """
        if not self.feature_stats:
            return 0.0

        features = self._extract_features(contract)

        # Calculate z-scores
        mean = self.feature_stats['mean']
        std = self.feature_stats['std'] + 1e-10

        z_scores = np.abs((features - mean) / std)

        # Anomaly score based on max z-score
        max_z = np.max(z_scores)

        # Convert to [0, 1]
        score = min(max_z / 10, 1.0)

        return score

    def _extract_features(self, contract: Dict) -> np.ndarray:
        """Extract features for anomaly detection"""
        features = np.zeros(5)

        # Feature 0: Amount
        features[0] = np.log(contract.get('amount', 1) + 1)

        # Feature 1: Number of parties
        features[1] = len(contract.get('parties', []))

        # Feature 2: Gas estimate
        features[2] = np.log(contract.get('gas_estimate', 1) + 1)

        # Feature 3: Execution time
        features[3] = contract.get('execution_time', 0)

        # Feature 4: Number of conditions
        features[4] = len(contract.get('conditions', []))

        return features
