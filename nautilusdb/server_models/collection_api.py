from typing import Dict, List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.column_type import ColumnType


class CreateCollectionRequest(BaseModel):
    name: str
    dimension: int
    description: Optional[str] = None
    metas: Optional[Dict[str, ColumnType]] = None


class DeleteCollectionRequest(BaseModel):
    name: str


class ListCollectionsResponse(BaseModel):
    names: List[str]


class DescribeCollectionRequest(BaseModel):
    collection_name: str


class DescribeCollectionResponse(BaseModel):
    collection_name: str
    dimension: int
    vector_count: int
    metric: str = 'l2'
    metas: Optional[Dict[str, ColumnType]] = None


class DeleteVectorsRequest(BaseModel):
    """
    Delete vectors in a collection by ids, all or by where clause. Exactly one
    of these three fields can be specified.
    """
    collection_name: str
    vector_ids: Optional[List[str]] = None
    delete_all: bool = False
    where: Optional[str] = None


class DeleteVectorsResponse(BaseModel):
    pass
