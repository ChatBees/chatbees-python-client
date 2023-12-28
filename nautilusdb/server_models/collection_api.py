from typing import Dict, List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.column_type import ColumnType


class CollectionBaseRequest(BaseModel):
    namespace_name: str
    collection_name: str


class CreateCollectionRequest(CollectionBaseRequest):
    description: Optional[str] = None


class DeleteCollectionRequest(CollectionBaseRequest):
    pass


class ListCollectionsRequest(BaseModel):
    namespace_name: str


class ListCollectionsResponse(BaseModel):
    names: List[str]


class DescribeCollectionRequest(CollectionBaseRequest):
    pass


class DescribeCollectionResponse(BaseModel):
    description: Optional[str] = None


class DeleteVectorsRequest(CollectionBaseRequest):
    """
    Delete vectors in a collection by ids, all or by where clause. Exactly one
    of these three fields can be specified.
    """
    vector_ids: Optional[List[str]] = None
    delete_all: bool = False
    where: Optional[str] = None


class DeleteVectorsResponse(BaseModel):
    pass
