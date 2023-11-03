from typing import Dict, Any, List, Optional

from pydantic import BaseModel

__all__ = ["Vector", "VectorResult"]


class Vector(BaseModel):
    """
    A Vector is a document with embeddings and an optional set of key-value
    properties (metadata).
    """

    # ID of the vector
    vid: str

    # Embedding of the vector.
    #
    # Embedding dimension must be identical to the embedding dimension
    # configured for its collection.
    embedding: Optional[List[float]] = None

    # Metadata associated with this vector.
    metadata: Optional[Dict[str, Any]] = None


class VectorResult(Vector):
    """
    Vector with a numeric relevance score.
    """

    # A numeric score to denote the relative relevance of this vector to the
    # given query. Higher score indicates more relevant vector.
    # Score is currently set to 1/(1 + l2_dist) between the vector and query
    # vector.
    score: float

