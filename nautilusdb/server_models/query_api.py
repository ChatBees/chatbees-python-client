from typing import List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.search import (
    SearchRequest as ClientQueryRequest,
    SearchResponse as ClientQueryResponse,
)
from nautilusdb.server_models.vector_api import VectorWithScore


class QueryResult(BaseModel):
    vectors: List[VectorWithScore]

    def to_client_response(self) -> ClientQueryResponse:
        return ClientQueryResponse(
            vectors=[v.to_client_vector_resut() for v in self.vectors])


class Query(BaseModel):
    # where supports SQL =, <, >, <=, >=, !=, and, or, etc.
    where: Optional[str] = None
    return_metas: Optional[List[str]] = None
    return_embedding: Optional[bool] = False
    top_k: Optional[int] = 3


class QueryWithEmbedding(Query):
    embedding: List[float]

    @classmethod
    def from_client_request(
        cls,
        req: ClientQueryRequest
    ) -> "QueryWithEmbedding":
        return QueryWithEmbedding(
            embedding=req.embedding,
            where=req.metadata_filter,
            return_metas=req.include_metadata,
            return_embedding=req.include_values,
            top_k=req.top_k
        )


class QueryRequest(BaseModel):
    collection_name: str
    queries: List[QueryWithEmbedding]


class QueryResponse(BaseModel):
    # The results are sorted by the score in the descending order
    results: List[QueryResult]
