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


