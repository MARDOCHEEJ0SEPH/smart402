"""
Semantic Graph Construction

Builds knowledge graphs for AI understanding using:
- Cosine similarity for semantic relationships
- Spectral clustering for concept grouping
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class GraphNode:
    """Node in semantic graph"""
    id: str
    concept: str
    embedding: np.ndarray
    metadata: Dict


@dataclass
class GraphEdge:
    """Edge in semantic graph"""
    source: str
    target: str
    weight: float
    relationship: str


class SemanticGraphBuilder:
    """
    Construct knowledge graph for AI understanding

    Graph G = (V, E, W)
    where:
    - V = vertices (contract concepts)
    - E = edges (relationships)
    - W = weights (semantic similarity)

    Semantic similarity:
    sim(c₁, c₂) = cos(v₁, v₂) = (v₁ · v₂)/(||v₁|| ||v₂||)
    """

    def __init__(self, embedding_dim: int = 128, similarity_threshold: float = 0.5):
        """
        Initialize semantic graph builder

        Args:
            embedding_dim: Dimension of embeddings
            similarity_threshold: Minimum similarity for edge creation
        """
        self.embedding_dim = embedding_dim
        self.similarity_threshold = similarity_threshold
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.adjacency_matrix: Optional[np.ndarray] = None

    def build_semantic_graph(self, contracts: List[Dict]) -> Dict:
        """
        Construct semantic graph from contracts

        Args:
            contracts: List of contract data

        Returns:
            Graph data structure
        """
        # Create nodes
        for contract in contracts:
            node_id = contract.get('id', str(len(self.nodes)))
            concept = contract.get('type', 'contract')

            # Generate embedding (simplified - would use actual embedding model)
            embedding = self._generate_embedding(contract)

            node = GraphNode(
                id=node_id,
                concept=concept,
                embedding=embedding,
                metadata=contract
            )

            self.nodes[node_id] = node

        # Build adjacency matrix
        n = len(self.nodes)
        self.adjacency_matrix = np.zeros((n, n))

        node_list = list(self.nodes.values())

        for i, node_i in enumerate(node_list):
            for j, node_j in enumerate(node_list):
                if i < j:  # Upper triangle only
                    similarity = self.cosine_similarity(
                        node_i.embedding,
                        node_j.embedding
                    )

                    if similarity > self.similarity_threshold:
                        self.adjacency_matrix[i][j] = similarity
                        self.adjacency_matrix[j][i] = similarity

                        # Create edge
                        edge = GraphEdge(
                            source=node_i.id,
                            target=node_j.id,
                            weight=similarity,
                            relationship='similar_to'
                        )
                        self.edges.append(edge)

        # Apply spectral clustering
        clusters = self._spectral_clustering()

        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'adjacency_matrix': self.adjacency_matrix,
            'clusters': clusters
        }

    def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate cosine similarity

        sim(v₁, v₂) = (v₁ · v₂) / (||v₁|| ||v₂||)

        Args:
            v1: First vector
            v2: Second vector

        Returns:
            Similarity score [0, 1]
        """
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Normalize to [0, 1]
        return (similarity + 1) / 2

    def _generate_embedding(self, contract: Dict) -> np.ndarray:
        """
        Generate embedding for contract
        (Simplified - would use actual transformer model)

        Args:
            contract: Contract data

        Returns:
            Embedding vector
        """
        # Use hash-based embedding for now
        import hashlib

        # Create feature string
        features = []
        for key in ['type', 'description', 'terms']:
            if key in contract:
                features.append(str(contract[key]))

        feature_str = '|'.join(features)

        # Generate deterministic embedding
        hash_obj = hashlib.sha256(feature_str.encode())
        hash_bytes = hash_obj.digest()

        # Convert to normalized embedding
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8)[:self.embedding_dim]
        embedding = embedding.astype(np.float32) / 255.0

        # Pad if necessary
        if len(embedding) < self.embedding_dim:
            embedding = np.pad(
                embedding,
                (0, self.embedding_dim - len(embedding)),
                mode='constant'
            )

        return embedding

    def _spectral_clustering(self, n_clusters: int = 3) -> Dict[str, int]:
        """
        Apply spectral clustering for concept grouping

        L = D - A (Laplacian matrix)
        where D is degree matrix

        Args:
            n_clusters: Number of clusters

        Returns:
            Node to cluster mapping
        """
        if self.adjacency_matrix is None or len(self.nodes) == 0:
            return {}

        A = self.adjacency_matrix
        n = A.shape[0]

        # Calculate degree matrix
        D = np.diag(np.sum(A, axis=1))

        # Laplacian matrix
        L = D - A

        # Eigendecomposition
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(L)

            # Use first k eigenvectors
            k = min(n_clusters, n)
            feature_vectors = eigenvectors[:, :k]

            # Simple k-means clustering (simplified)
            clusters = self._kmeans(feature_vectors, n_clusters)

            # Map node IDs to clusters
            node_list = list(self.nodes.keys())
            cluster_map = {
                node_list[i]: int(clusters[i])
                for i in range(len(node_list))
            }

            return cluster_map

        except np.linalg.LinAlgError:
            # Fallback: random assignment
            node_list = list(self.nodes.keys())
            return {
                node: np.random.randint(0, n_clusters)
                for node in node_list
            }

    def _kmeans(self, X: np.ndarray, k: int, max_iters: int = 100) -> np.ndarray:
        """
        Simple k-means clustering

        Args:
            X: Feature vectors
            k: Number of clusters
            max_iters: Maximum iterations

        Returns:
            Cluster assignments
        """
        n = X.shape[0]

        if n < k:
            return np.arange(n)

        # Initialize centroids randomly
        indices = np.random.choice(n, k, replace=False)
        centroids = X[indices]

        for _ in range(max_iters):
            # Assign to nearest centroid
            distances = np.linalg.norm(
                X[:, np.newaxis] - centroids,
                axis=2
            )
            clusters = np.argmin(distances, axis=1)

            # Update centroids
            new_centroids = np.array([
                X[clusters == i].mean(axis=0) if np.any(clusters == i) else centroids[i]
                for i in range(k)
            ])

            # Check convergence
            if np.allclose(centroids, new_centroids):
                break

            centroids = new_centroids

        return clusters

    def get_related_contracts(self, contract_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Get most related contracts by similarity

        Args:
            contract_id: Source contract ID
            top_k: Number of results

        Returns:
            List of (contract_id, similarity) tuples
        """
        if contract_id not in self.nodes:
            return []

        source_node = self.nodes[contract_id]
        similarities = []

        for node_id, node in self.nodes.items():
            if node_id != contract_id:
                sim = self.cosine_similarity(
                    source_node.embedding,
                    node.embedding
                )
                similarities.append((node_id, sim))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]
