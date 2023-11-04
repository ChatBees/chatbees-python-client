from typing import List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.search import (
    SearchRequest as ClientSearchRequest,
    SearchResponse as ClientSearchResponse,
)
from nautilusdb.server_models.vector_api import VectorWithScore


class SearchResult(BaseModel):
    vectors: List[VectorWithScore]

    def to_client_response(self) -> ClientSearchResponse:
        return ClientSearchResponse(
            vectors=[v.to_client_vector_resut() for v in self.vectors])


class Search(BaseModel):
    # where supports SQL =, <, >, <=, >=, !=, and, or, etc.
    where: Optional[str] = None
    return_metas: Optional[List[str]] = None
    return_embedding: Optional[bool] = False
    top_k: Optional[int] = 3


class SearchWithEmbedding(Search):
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


class SearchRequest(BaseModel):
    collection_name: str
    queries: List[SearchWithEmbedding]


class SearchResponse(BaseModel):
    # The results are sorted by the score in the descending order
    results: List[SearchResult]
