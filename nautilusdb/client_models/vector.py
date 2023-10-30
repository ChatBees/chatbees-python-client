from typing import Optional, Dict, Any, List

from pydantic import BaseModel

from nautilusdb.server_models.index import Vector as ServerVector

__all__ = ["Vector"]


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
    embedding: List[float] = None

    # Metadata associated with this vector.
    metadata: Dict[str, Any] = None

    def to_api_vector(self) -> ServerVector:
        if self.vid is None or self.vid == "":
            raise ValueError("Cannot create vector without a name")
        if self.embedding is None:
            raise ValueError("Cannot create vector without embeddings")
        return ServerVector(
            id=self.vid,
            embedding=self.embedding,
            metas=self.metadata)
