"""
AEO Scoring Algorithm

Calculates AI visibility score for contracts:
AEO Score = Σᵢ wᵢ * fᵢ(contract)

where:
f₁ = Semantic Relevance Score
f₂ = Citation Frequency
f₃ = Content Freshness
f₄ = Authority Score
f₅ = Cross-Platform Presence
"""

import numpy as np
from typing import Dict, List
from collections import Counter
import hashlib
from datetime import datetime, timedelta


class AEOScorer:
    """
    Calculate AEO scores for contract visibility
    """

    def __init__(self):
        """Initialize AEO scorer"""
        self.weights = [0.3, 0.25, 0.15, 0.2, 0.1]  # Σw = 1
        self.citation_history: Dict[str, List[float]] = {}
        self.authority_graph: Dict[str, List[str]] = {}

    def calculate_aeo_score(self, contract: Dict) -> float:
        """
        Calculate comprehensive AEO score

        AEO Score = Σᵢ wᵢ * fᵢ(contract)

        Args:
            contract: Contract data

        Returns:
            AEO score [0, 1]
        """
        f1 = self.semantic_relevance(contract)
        f2 = self.citation_frequency(contract)
        f3 = self.content_freshness(contract)
        f4 = self.authority_score(contract)
        f5 = self.cross_platform_presence(contract)

        scores = [f1, f2, f3, f4, f5]

        # Weighted combination
        aeo_score = sum(w * f for w, f in zip(self.weights, scores))

        return aeo_score

    def semantic_relevance(self, contract: Dict) -> float:
        """
        Calculate semantic relevance score using TF-IDF

        SRS = Σⱼ (TF-IDF(termⱼ) * relevance(termⱼ, query))
        where TF-IDF = tf(t,d) * log(N/df(t))

        Args:
            contract: Contract data

        Returns:
            Semantic relevance score [0, 1]
        """
        text = self._extract_text(contract)
        if not text:
            return 0.0

        # Tokenize
        tokens = text.lower().split()

        # Calculate term frequency
        tf = Counter(tokens)
        max_freq = max(tf.values()) if tf else 1

        # Normalize TF
        tf_normalized = {term: freq / max_freq for term, freq in tf.items()}

        # Important contract terms (higher relevance)
        important_terms = {
            'payment', 'contract', 'party', 'obligation',
            'smart', 'blockchain', 'execute', 'settlement'
        }

        # Calculate relevance
        relevance = 0.0
        for term, tf_val in tf_normalized.items():
            # Boost for important terms
            boost = 2.0 if term in important_terms else 1.0
            relevance += tf_val * boost

        # Normalize to [0, 1]
        relevance = min(relevance / len(tokens), 1.0) if tokens else 0.0

        return relevance

    def citation_frequency(self, contract: Dict) -> float:
        """
        Calculate citation frequency with time decay

        CF = (citations_7d / total_queries_7d) * time_decay_factor
        time_decay_factor = e^(-λt), where λ = 0.1, t = days_since_citation

        Args:
            contract: Contract data

        Returns:
            Citation frequency score [0, 1]
        """
        contract_id = contract.get('id', 'unknown')

        # Get citation history
        citations = self.citation_history.get(contract_id, [])

        if not citations:
            return 0.0

        # Calculate time decay
        now = datetime.now().timestamp()
        lambda_decay = 0.1

        weighted_citations = 0.0
        for citation_time in citations:
            days_since = (now - citation_time) / 86400  # Convert to days
            decay = np.exp(-lambda_decay * days_since)
            weighted_citations += decay

        # Normalize (assume 100 queries per day as baseline)
        baseline_queries = 100 * 7
        citation_freq = weighted_citations / baseline_queries

        return min(citation_freq, 1.0)

    def content_freshness(self, contract: Dict) -> float:
        """
        Calculate content freshness using sigmoid

        F = 1 / (1 + e^(-k(t - t₀)))

        where:
        - k = steepness parameter
        - t = current_time
        - t₀ = last_update

        Args:
            contract: Contract data

        Returns:
            Freshness score [0, 1]
        """
        last_update = contract.get('last_update', datetime.now().timestamp())
        current_time = datetime.now().timestamp()

        # Days since update
        days_since_update = (current_time - last_update) / 86400

        # Sigmoid parameters
        k = 0.1  # Steepness
        t0 = 30  # Half-life at 30 days

        # Inverted sigmoid (fresh = high score)
        freshness = 1 / (1 + np.exp(k * (days_since_update - t0)))

        return freshness

    def authority_score(self, contract: Dict) -> float:
        """
        Calculate authority score using PageRank-inspired algorithm

        AS(C) = (1-d) + d * Σ(AS(Cᵢ)/L(Cᵢ))

        where:
        - d = damping factor (0.85)
        - L = number of outgoing links

        Args:
            contract: Contract data

        Returns:
            Authority score [0, 1]
        """
        contract_id = contract.get('id', 'unknown')

        # Damping factor
        d = 0.85

        # Get incoming links
        incoming = []
        for node, links in self.authority_graph.items():
            if contract_id in links:
                incoming.append(node)

        if not incoming:
            return 1 - d  # Base authority

        # Calculate authority from incoming links
        authority = 1 - d

        for node in incoming:
            outgoing_count = len(self.authority_graph.get(node, []))
            if outgoing_count > 0:
                # Simplified PageRank (would need iteration in full version)
                authority += d * (1.0 / outgoing_count)

        return min(authority, 1.0)

    def cross_platform_presence(self, contract: Dict) -> float:
        """
        Calculate cross-platform presence score

        CPP = Σₚ (presence(p) * weight(p))

        where p ∈ {ChatGPT, Claude, Perplexity, ...}

        Args:
            contract: Contract data

        Returns:
            Cross-platform presence score [0, 1]
        """
        platforms = contract.get('platforms', [])

        # Platform weights
        platform_weights = {
            'chatgpt': 0.35,
            'claude': 0.35,
            'perplexity': 0.15,
            'gemini': 0.10,
            'other': 0.05
        }

        presence = 0.0
        for platform in platforms:
            weight = platform_weights.get(platform.lower(), 0.0)
            presence += weight

        return min(presence, 1.0)

    def _extract_text(self, contract: Dict) -> str:
        """
        Extract text from contract for analysis

        Args:
            contract: Contract data

        Returns:
            Concatenated text
        """
        text_parts = []

        # Extract various fields
        for key in ['description', 'terms', 'conditions', 'parties']:
            if key in contract:
                value = contract[key]
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend(str(v) for v in value)

        return ' '.join(text_parts)

    def add_citation(self, contract_id: str, timestamp: Optional[float] = None):
        """
        Record a citation for a contract

        Args:
            contract_id: Contract identifier
            timestamp: Citation timestamp (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()

        if contract_id not in self.citation_history:
            self.citation_history[contract_id] = []

        self.citation_history[contract_id].append(timestamp)

    def add_link(self, from_contract: str, to_contract: str):
        """
        Add authority link between contracts

        Args:
            from_contract: Source contract
            to_contract: Target contract
        """
        if from_contract not in self.authority_graph:
            self.authority_graph[from_contract] = []

        self.authority_graph[from_contract].append(to_contract)
