from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel


"""
A vector has 4 attributes: a unique id, embedding, a vector id and metadatas.
"""


class Vector(BaseModel):
    id: str
    embedding: Optional[List[float]] = None
    metas: Optional[Dict[str, Any]] = None


class VectorWithScore(Vector):
    score: float


class Query(BaseModel):
    # where supports SQL =, <, >, <=, >=, !=, and, or, etc.
    where: Optional[str] = None
    return_metas: Optional[List[str]] = None
    return_embedding: Optional[bool] = False
    top_k: Optional[int] = 3


class QueryWithEmbedding(Query):
    embedding: List[float]


class QueryResult(BaseModel):
    vectors: List[VectorWithScore]
