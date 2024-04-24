from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, model_validator


__all__ = [
    "IngestionType",
    "IngestionSpec",
    "ConfluenceSpec",
    "GDriveSpec",
    "NotionSpec",
]

class IngestionType(Enum):
    CONFLUENCE = 'CONFLUENCE'
    GDRIVE = 'GDRIVE'
    NOTION = 'NOTION'


class IngestionSpec(BaseModel):
    # API token for crawling. If not set, use existing connector.
    token: Optional[str] = None


class ConfluenceSpec(IngestionSpec):
    url: str
    # if you connect Confluence via OAuth, no need to set username.
    # if you don't connect via OAuth, you can pass a confluence user and api token.
    username: Optional[str] = None
    # Specify space to ingest all pages in the space, or cql to ingest the
    # selected pages. Please specify either space or cql, not both.
    space: Optional[str] = None
    cql: Optional[str] = None

    @model_validator(mode='after')
    def validate_input(self) -> 'ConfluenceSpec':
        if self.space is None and self.cql is None:
            raise ValueError("Please specify space or cql")
        if self.space is not None and self.cql is not None:
            raise ValueError("Please specify only space or cql, not both")
        return self


class GDriveSpec(IngestionSpec):
    folder_name: Optional[str] = None


class NotionSpec(IngestionSpec):
    page_ids: Optional[List[str]] = None
