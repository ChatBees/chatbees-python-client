from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from nautilusdb.client_models.vector import (
    Vector as ClientVector,
    VectorResult as ClientVectorResult,
)
from nautilusdb.server_models.collection_api import CollectionBaseRequest


class Vector(BaseModel):
    id: str
    embedding: Optional[List[float]] = None
    metas: Optional[Dict[str, Any]] = None

    @classmethod
    def from_client_vector(cls, vector: ClientVector) -> "Vector":
        if vector.vid is None or vector.vid == "":
            raise ValueError("Cannot create vector without a name")
        if vector.embedding is None:
            raise ValueError("Cannot create vector without embeddings")
        return Vector(
            id=vector.vid,
            embedding=vector.embedding,
            metas=vector.metadata)


class VectorWithScore(Vector):
    score: float

    def to_client_vector_request(self):
        return ClientVectorResult(
            score=self.score,
            vid=self.id,
            embedding=self.embedding,
            metadata=self.metas
        )


class UpsertRequest(CollectionBaseRequest):
    vectors: List[Vector]


class UpsertResponse(BaseModel):
    upsert_count: int
