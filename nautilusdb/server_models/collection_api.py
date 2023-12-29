from typing import Dict, List, Optional

from pydantic import BaseModel


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
