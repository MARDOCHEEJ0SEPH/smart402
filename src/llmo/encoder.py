"""
Contract Encoder for Universal LLM Format
"""

import numpy as np
from typing import Dict, List


class ContractEncoder:
    """
    Encode contracts into universal LLM format

    Using Transformer architecture:
    Encoding = TransformerEncoder(X + PE)

    where:
    - X = token embeddings
    - PE = positional encoding

    PE(pos, 2i) = sin(pos/10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos/10000^(2i/d_model))
    """

    def __init__(self, d_model: int = 128, max_len: int = 512):
        """
        Initialize contract encoder

        Args:
            d_model: Model dimension
            max_len: Maximum sequence length
        """
        self.d_model = d_model
        self.max_len = max_len
        self.word_embeddings: Dict[str, np.ndarray] = {}
        self.positional_encoding = self._create_positional_encoding()

    def encode_contract_for_llm(self, contract: Dict) -> np.ndarray:
        """
        Encode contract into universal format

        Args:
            contract: Contract data

        Returns:
            Encoded representation
        """
        # Extract text
        text = self._contract_to_text(contract)

        # Tokenize
        tokens = text.split()[:self.max_len]

        # Get embeddings
        embeddings = []
        for token in tokens:
            emb = self._get_token_embedding(token, contract)
            embeddings.append(emb)

        if not embeddings:
            return np.zeros((1, self.d_model))

        # Convert to array
        embeddings = np.array(embeddings)

        # Add positional encoding
        n_tokens = len(embeddings)
        pos_enc = self.positional_encoding[:n_tokens]

        # Combine
        encoded = embeddings + pos_enc

        return encoded

    def _create_positional_encoding(self) -> np.ndarray:
        """
        Create positional encoding matrix

        PE(pos, 2i) = sin(pos/10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos/10000^(2i/d_model))

        Returns:
            Positional encoding matrix
        """
        pe = np.zeros((self.max_len, self.d_model))
        position = np.arange(self.max_len)[:, np.newaxis]
        div_term = np.exp(
            np.arange(0, self.d_model, 2) * -(np.log(10000.0) / self.d_model)
        )

        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)

        return pe

    def _get_token_embedding(self, token: str, contract: Dict) -> np.ndarray:
        """
        Get embedding for token with contract-specific features

        Args:
            token: Token string
            contract: Contract context

        Returns:
            Token embedding
        """
        # Check cache
        if token in self.word_embeddings:
            base_emb = self.word_embeddings[token]
        else:
            # Generate embedding
            base_emb = self._generate_embedding(token)
            self.word_embeddings[token] = base_emb

        # Extract contract-specific features
        features = self._extract_token_features(token, contract)

        # Combine
        combined = 0.8 * base_emb + 0.2 * features

        return combined

    def _generate_embedding(self, token: str) -> np.ndarray:
        """
        Generate base embedding for token

        Args:
            token: Token string

        Returns:
            Embedding vector
        """
        # Hash-based embedding
        import hashlib

        hash_obj = hashlib.sha256(token.encode())
        hash_bytes = hash_obj.digest()

        # Convert to embedding
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8)[:self.d_model]
        embedding = embedding.astype(np.float32) / 255.0

        # Pad if necessary
        if len(embedding) < self.d_model:
            embedding = np.pad(
                embedding,
                (0, self.d_model - len(embedding)),
                mode='constant'
            )

        # Normalize
        embedding = embedding / (np.linalg.norm(embedding) + 1e-10)

        return embedding

    def _extract_token_features(self, token: str, contract: Dict) -> np.ndarray:
        """
        Extract contract-specific features for token

        Args:
            token: Token string
            contract: Contract context

        Returns:
            Feature vector
        """
        features = np.zeros(self.d_model)

        # Feature 0: Is party name
        parties = contract.get('parties', [])
        if token in ' '.join(parties):
            features[0] = 1.0

        # Feature 1: Is amount
        amount_str = str(contract.get('amount', ''))
        if token in amount_str:
            features[1] = 1.0

        # Feature 2: Token length (normalized)
        features[2] = len(token) / 20.0

        # Feature 3: Is uppercase
        features[3] = 1.0 if token.isupper() else 0.0

        # Feature 4: Contains digits
        features[4] = 1.0 if any(c.isdigit() for c in token) else 0.0

        return features

    def _contract_to_text(self, contract: Dict) -> str:
        """
        Convert contract to text representation

        Args:
            contract: Contract data

        Returns:
            Text representation
        """
        parts = []

        # Add type
        if 'type' in contract:
            parts.append(f"Contract Type: {contract['type']}")

        # Add parties
        if 'parties' in contract:
            parties_str = ', '.join(contract['parties'])
            parts.append(f"Parties: {parties_str}")

        # Add amount
        if 'amount' in contract:
            parts.append(f"Amount: {contract['amount']}")

        # Add terms
        if 'terms' in contract:
            parts.append(f"Terms: {contract['terms']}")

        # Add description
        if 'description' in contract:
            parts.append(f"Description: {contract['description']}")

        return '. '.join(parts)
