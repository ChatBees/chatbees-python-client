from typing import Optional, Dict, Any, List

from server_models.index import Vector as ServerVector


class Vector:
    """
    Client-side vector to decouple from API vector
    """

    id: str
    embedding: Optional[List[float]]
    metadata: Optional[Dict[str, Any]]

    def __init__(self, id, embedding=None, metadata=None):
        self.id = id
        self.embedding = embedding
        self.metadata = metadata

    def to_api_vector(self) -> ServerVector:
        return ServerVector(id=self.id, embedding=self.embedding,
                         metas=self.metadata)
