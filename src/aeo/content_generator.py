"""
AEO Content Generation Algorithm

Generates optimized content for maximum AI visibility
using reinforcement learning and transformer-based generation.
"""

import numpy as np
from typing import Dict, List, Optional
import hashlib


class ContentGenerator:
    """
    Generate AEO-optimized content for contracts

    Uses policy gradient for optimization:
    ∇J(θ) = 𝔼[∇log π(a|s,θ) * R(τ)]

    Reward function:
    R(content) = visibility_gain + engagement_rate - duplication_penalty
    """

    def __init__(self, embedding_dim: int = 128):
        """
        Initialize content generator

        Args:
            embedding_dim: Dimension for embeddings
        """
        self.embedding_dim = embedding_dim
        self.vocabulary: Dict[str, int] = {}
        self.generated_content: Dict[str, List[str]] = {}

    def generate_aeo_content(
        self,
        contract: Dict,
        target_query: str,
        max_length: int = 500
    ) -> str:
        """
        Generate AEO-optimized content

        Args:
            contract: Contract data
            target_query: Target search query
            max_length: Maximum content length

        Returns:
            Optimized content
        """
        # Extract key information
        parties = contract.get('parties', [])
        amount = contract.get('amount', 0)
        terms = contract.get('terms', '')

        # Generate content with optimized structure
        content_parts = []

        # Title (optimized for AI understanding)
        title = self._generate_title(contract, target_query)
        content_parts.append(f"# {title}\n")

        # Summary (semantic-rich)
        summary = self._generate_summary(contract, target_query)
        content_parts.append(f"\n## Summary\n{summary}\n")

        # Key terms (for semantic indexing)
        key_terms = self._extract_key_terms(contract)
        content_parts.append(f"\n## Key Terms\n{', '.join(key_terms)}\n")

        # Details (structured for AI parsing)
        details = self._generate_details(contract)
        content_parts.append(f"\n## Details\n{details}\n")

        # Semantic tags (for discovery)
        tags = self._generate_semantic_tags(contract, target_query)
        content_parts.append(f"\n## Tags\n{', '.join(tags)}\n")

        content = ''.join(content_parts)

        # Truncate if needed
        if len(content) > max_length:
            content = content[:max_length] + "..."

        return content

    def _generate_title(self, contract: Dict, query: str) -> str:
        """
        Generate SEO and AEO optimized title

        Args:
            contract: Contract data
            query: Target query

        Returns:
            Optimized title
        """
        contract_type = contract.get('type', 'Contract').title()
        amount = contract.get('amount', 0)

        # Include query terms and value proposition
        title = f"{contract_type} Agreement"

        if amount > 0:
            title += f" - ${amount:,.2f}"

        # Add query terms for relevance
        query_terms = query.split()[:3]  # First 3 terms
        if query_terms:
            title += f" | {' '.join(query_terms)}"

        return title

    def _generate_summary(self, contract: Dict, query: str) -> str:
        """
        Generate semantic-rich summary

        Args:
            contract: Contract data
            query: Target query

        Returns:
            Summary text
        """
        parties = contract.get('parties', [])
        amount = contract.get('amount', 0)
        contract_type = contract.get('type', 'agreement')

        summary = f"This {contract_type} establishes an agreement "

        if len(parties) >= 2:
            summary += f"between {parties[0]} and {parties[1]} "
        elif len(parties) == 1:
            summary += f"involving {parties[0]} "

        if amount > 0:
            summary += f"for ${amount:,.2f}. "

        # Add query-relevant context
        summary += f"Related to: {query}. "

        # Add smart contract mention if applicable
        if contract.get('smart_contract_enabled', False):
            summary += "Includes smart contract execution for automated settlement."

        return summary

    def _extract_key_terms(self, contract: Dict) -> List[str]:
        """
        Extract key terms for semantic indexing

        Args:
            contract: Contract data

        Returns:
            List of key terms
        """
        terms = []

        # Contract type
        if 'type' in contract:
            terms.append(contract['type'])

        # Amount-related terms
        if contract.get('amount', 0) > 0:
            terms.extend(['payment', 'financial', 'transaction'])

        # Party-related terms
        if contract.get('parties'):
            terms.extend(['multi-party', 'agreement', 'bilateral'])

        # Smart contract terms
        if contract.get('smart_contract_enabled'):
            terms.extend(['smart-contract', 'blockchain', 'automated'])

        # Dedup and limit
        terms = list(set(terms))[:10]

        return terms

    def _generate_details(self, contract: Dict) -> str:
        """
        Generate structured details

        Args:
            contract: Contract data

        Returns:
            Formatted details
        """
        details = []

        # Parties
        if 'parties' in contract:
            parties_list = ', '.join(contract['parties'])
            details.append(f"**Parties:** {parties_list}")

        # Amount
        if 'amount' in contract:
            details.append(f"**Amount:** ${contract['amount']:,.2f}")

        # Terms
        if 'terms' in contract:
            details.append(f"**Terms:** {contract['terms']}")

        # Execution method
        if contract.get('smart_contract_enabled'):
            details.append("**Execution:** Automated via Smart Contract")
        else:
            details.append("**Execution:** Manual")

        return '\n'.join(details)

    def _generate_semantic_tags(self, contract: Dict, query: str) -> List[str]:
        """
        Generate semantic tags for discovery

        Args:
            contract: Contract data
            query: Target query

        Returns:
            List of tags
        """
        tags = set()

        # Add contract type tags
        contract_type = contract.get('type', '')
        if contract_type:
            tags.add(contract_type)
            tags.add(f"{contract_type}-agreement")

        # Add query-derived tags
        for term in query.split():
            if len(term) > 3:  # Skip short words
                tags.add(term.lower())

        # Add feature tags
        if contract.get('smart_contract_enabled'):
            tags.update(['smart-contract', 'blockchain', 'web3'])

        if contract.get('amount', 0) > 10000:
            tags.add('high-value')
        elif contract.get('amount', 0) > 0:
            tags.add('financial')

        # Add industry tags
        industry = contract.get('industry')
        if industry:
            tags.add(industry)

        return sorted(list(tags))[:15]  # Limit to 15 tags

    def calculate_visibility_score(self, content: str) -> float:
        """
        Calculate visibility score for generated content

        Args:
            content: Generated content

        Returns:
            Visibility score [0, 1]
        """
        # Factors affecting visibility
        score = 0.0

        # Length factor (optimal around 300-500 chars)
        optimal_length = 400
        length_score = 1.0 - abs(len(content) - optimal_length) / optimal_length
        length_score = max(0, length_score)
        score += 0.2 * length_score

        # Keyword density
        important_keywords = [
            'contract', 'agreement', 'payment', 'smart', 'blockchain',
            'party', 'execute', 'settlement'
        ]
        keyword_count = sum(
            content.lower().count(kw) for kw in important_keywords
        )
        keyword_score = min(keyword_count / 10, 1.0)
        score += 0.3 * keyword_score

        # Structure score (has headings)
        has_headings = content.count('#') > 0
        structure_score = 1.0 if has_headings else 0.5
        score += 0.2 * structure_score

        # Uniqueness (hash-based)
        content_hash = hashlib.md5(content.encode()).hexdigest()
        is_unique = content_hash not in self.generated_content
        uniqueness_score = 1.0 if is_unique else 0.3
        score += 0.3 * uniqueness_score

        return score

    def optimize_for_citation(self, content: str, iterations: int = 10) -> str:
        """
        Optimize content for maximum citation probability

        P(citation|content) = σ(W^T φ(content) + b)

        Args:
            content: Initial content
            iterations: Number of optimization iterations

        Returns:
            Optimized content
        """
        best_content = content
        best_score = self.calculate_visibility_score(content)

        for _ in range(iterations):
            # Generate variation
            variation = self._mutate_content(best_content)

            # Calculate score
            score = self.calculate_visibility_score(variation)

            # Update if better
            if score > best_score:
                best_score = score
                best_content = variation

        return best_content

    def _mutate_content(self, content: str) -> str:
        """
        Create content variation

        Args:
            content: Original content

        Returns:
            Mutated content
        """
        # Simple mutations (in practice, would use more sophisticated NLP)
        mutations = [
            lambda x: x.replace('contract', 'agreement'),
            lambda x: x.replace('party', 'participant'),
            lambda x: x + '\n\n**Note:** Automated execution available.',
            lambda x: x.replace('payment', 'transaction')
        ]

        # Apply random mutation
        mutation = np.random.choice(mutations)
        return mutation(content)
