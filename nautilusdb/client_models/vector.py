from typing import Optional, Dict, Any, List

from nautilusdb.server_models.index import Vector as ServerVector

__all__ = ["Vector"]


class Vector:
    """
    A Vector is a document with embeddings and an optional set of key-value
    properties (metadata).
    """

    vid: str
    embedding: Optional[List[float]]
    metadata: Optional[Dict[str, Any]]

    def __init__(
        self, vid: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a vector

        :param vid: ID of the vector
        :param embedding: Embedding of the vector. Embedding dimension must be
                          identical to the embedding dimension configured for
                          its collection.
        :param metadata: Metadata associated with this vector.
        """
        self.vid = vid
        self.embedding = embedding
        self.metadata = metadata

    def to_api_vector(self) -> ServerVector:
        if self.vid is None or self.vid == "":
            raise ValueError("Cannot create vector without a name")
        if self.embedding is None:
            raise ValueError("Cannot create vector without embeddings")
        return ServerVector(
            id=self.vid,
            embedding=self.embedding,
            metas=self.metadata)
