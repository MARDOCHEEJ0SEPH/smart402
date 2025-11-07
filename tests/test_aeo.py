"""
Tests for AEO module
"""

import pytest
from src.aeo.scoring import AEOScorer
from src.aeo.content_generator import ContentGenerator
from src.aeo.semantic_graph import SemanticGraphBuilder


class TestAEOScorer:
    """Test AEO scoring"""

    def test_score_calculation(self):
        """Test AEO score calculation"""
        scorer = AEOScorer()
        contract = {
            'id': 'test_1',
            'description': 'payment contract between parties',
            'amount': 1000,
            'parties': ['party_a', 'party_b']
        }

        score = scorer.calculate_aeo_score(contract)
        assert 0 <= score <= 1

    def test_semantic_relevance(self):
        """Test semantic relevance scoring"""
        scorer = AEOScorer()
        contract = {
            'description': 'smart contract payment blockchain'
        }

        relevance = scorer.semantic_relevance(contract)
        assert 0 <= relevance <= 1


class TestContentGenerator:
    """Test content generation"""

    def test_content_generation(self):
        """Test AEO content generation"""
        generator = ContentGenerator()
        contract = {
            'id': 'test_1',
            'type': 'payment',
            'amount': 5000,
            'parties': ['alice', 'bob'],
            'terms': 'Payment upon delivery'
        }

        content = generator.generate_aeo_content(
            contract,
            target_query='smart contract payment'
        )

        assert len(content) > 0
        assert 'Payment' in content or 'payment' in content

    def test_visibility_score(self):
        """Test visibility score calculation"""
        generator = ContentGenerator()
        content = "# Smart Contract Payment\n\nThis contract involves payment between parties."

        score = generator.calculate_visibility_score(content)
        assert 0 <= score <= 1


class TestSemanticGraph:
    """Test semantic graph builder"""

    def test_graph_building(self):
        """Test semantic graph construction"""
        builder = SemanticGraphBuilder()
        contracts = [
            {'id': 'c1', 'type': 'payment', 'description': 'test 1'},
            {'id': 'c2', 'type': 'service', 'description': 'test 2'}
        ]

        graph = builder.build_semantic_graph(contracts)

        assert 'nodes' in graph
        assert 'edges' in graph
        assert len(graph['nodes']) == 2
