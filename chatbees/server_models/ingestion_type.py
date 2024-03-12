from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


__all__ = [
    "IngestionType",
    "IngestionSpec",
    "ConfluenceSpec",
]

class IngestionType(Enum):
    CONFLUENCE = 'CONFLUENCE'


class IngestionSpec(BaseModel):
    # API token for crawling. If not set, use existing connector.
    token: Optional[str] = None


class ConfluenceSpec(IngestionSpec):
    url: str
    space: str
    username: Optional[str] = None
