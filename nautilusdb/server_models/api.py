from typing import Dict, List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.column_type import ColumnType
from nautilusdb.server_models.index import (
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


class CreateApiKeyRequest(BaseModel):
    pass


class CreateApiKeyResponse(BaseModel):
    api_key: str
