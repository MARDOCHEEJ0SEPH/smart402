"""
Mathematical Utilities
"""

import numpy as np
from typing import List, Union


def softmax(x: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Softmax function

    Args:
        x: Input values

    Returns:
        Probability distribution
    """
    x = np.array(x)
    exp_x = np.exp(x - np.max(x))  # Numerical stability
    return exp_x / np.sum(exp_x)


def normalize(x: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Normalize vector to unit length

    Args:
        x: Input vector

    Returns:
        Normalized vector
    """
    x = np.array(x)
    norm = np.linalg.norm(x)

    if norm == 0:
        return x

    return x / norm


def cosine_similarity(
    v1: Union[np.ndarray, List[float]],
    v2: Union[np.ndarray, List[float]]
) -> float:
    """
    Calculate cosine similarity

    sim(v₁, v₂) = (v₁ · v₂) / (||v₁|| ||v₂||)

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Similarity [0, 1]
    """
    v1 = np.array(v1)
    v2 = np.array(v2)

    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot_product / (norm1 * norm2)

    # Normalize to [0, 1]
    return (similarity + 1) / 2


def sigmoid(x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Sigmoid function

    Args:
        x: Input value(s)

    Returns:
        Sigmoid output
    """
    return 1 / (1 + np.exp(-x))


def euclidean_distance(
    v1: Union[np.ndarray, List[float]],
    v2: Union[np.ndarray, List[float]]
) -> float:
    """
    Calculate Euclidean distance

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Distance
    """
    v1 = np.array(v1)
    v2 = np.array(v2)

    return float(np.linalg.norm(v1 - v2))
