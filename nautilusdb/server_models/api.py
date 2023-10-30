from typing import Dict, List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.column_type import ColumnType
from nautilusdb.server_models.index import (
    QueryWithEmbedding,
    QueryResult,
    Vector,
)


class CreateCollectionRequest(BaseModel):
    name: str
    dimension: int
    description: Optional[str] = None
    metas: Optional[Dict[str, ColumnType]] = None


class DeleteCollectionRequest(BaseModel):
    name: str


class ListCollectionsResponse(BaseModel):
    names: List[str]


class UpsertRequest(BaseModel):
    collection_name: str
    vectors: List[Vector]


class UpsertResponse(BaseModel):
    upsert_count: int


class QueryRequest(BaseModel):
    collection_name: str
    queries: List[QueryWithEmbedding]


class QueryResponse(BaseModel):
    # The results are sorted by the score in the descending order
    results: List[QueryResult]


class CreateApiKeyRequest(BaseModel):
    pass


class CreateApiKeyResponse(BaseModel):
    api_key: str
