from typing import List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.search import (
    SearchRequest as ClientSearchRequest,
)
from nautilusdb.client_models.query import (
    QueryRequest as ClientQueryRequest,
    VectorResponse as ClientVectorResponse,
)
from nautilusdb.server_models.collection_api import CollectionBaseRequest
from nautilusdb.server_models.vector_api import VectorWithScore


class VectorResult(BaseModel):
    vectors: List[VectorWithScore]

    def to_client_response(self) -> ClientVectorResponse:
        return ClientVectorResponse(
            vectors=[v.to_client_vector_request() for v in self.vectors])


class Query(BaseModel):
    # where supports SQL =, <, >, <=, >=, !=, and, or, etc.
    where: Optional[str] = None
    return_metas: Optional[List[str]] = None
    return_embedding: Optional[bool] = False
    top_k: Optional[int] = 3

    @classmethod
    def from_client_request(cls, req: ClientQueryRequest) -> "Query":
        return Query(
            where=req.metadata_filter,
            return_metas=req.include_metadata,
            return_embedding=req.include_values,
            top_k=req.top_k
        )


class SearchWithEmbedding(Query):
    embedding: List[float]

    @classmethod
    def from_client_request(
        cls,
        req: ClientSearchRequest
    ) -> "SearchWithEmbedding":
        return SearchWithEmbedding(
            embedding=req.embedding,
            where=req.metadata_filter,
            return_metas=req.include_metadata,
            return_embedding=req.include_values,
            top_k=req.top_k
        )


class SearchRequest(CollectionBaseRequest):
    queries: List[SearchWithEmbedding]


class SearchResponse(BaseModel):
    # The results are sorted by the score in the descending order
    results: List[VectorResult]
