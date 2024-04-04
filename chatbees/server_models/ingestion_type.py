from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


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
    space: str
    # if you connect Confluence via OAuth, no need to set username.
    # if you don't connect via OAuth, you can pass a confluence user and api token.
    username: Optional[str] = None


class GDriveSpec(IngestionSpec):
    folder_name: Optional[str] = None


class NotionSpec(IngestionSpec):
    page_ids: Optional[List[str]] = None
