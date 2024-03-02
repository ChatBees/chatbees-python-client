from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class CrawlType(Enum):
    WEBSITE = 'WEBSITE'
    SLACK = 'SLACK'
    NOTION = 'NOTION'
    CONFLUENCE = 'CONFLUENCE'


IngestType = CrawlType

__all__ = ["CrawlSpec", "WebsiteSpec", "ConfluenceSpec"]

class CrawlSpec(BaseModel):
    # API token for crawling. If not set, use existing connector.
    token: Optional[str] = None


class SlackSpec(CrawlSpec):
    channels: Optional[List[str]] = None


class NotionSpec(CrawlSpec):
    page_ids: Optional[List[str]] = None


class GDriveSpec(CrawlSpec):
    folder_name: Optional[str] = None


class WebsiteSpec(CrawlSpec):
    root_url: str
    max_urls_to_crawl: int


class ConfluenceSpec(CrawlSpec):
    url: str
    space: str
    username: Optional[str] = None
