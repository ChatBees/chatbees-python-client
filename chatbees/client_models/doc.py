__all__ = ["AnswerReference", "CrawlStatus", "SearchReference"]

from enum import Enum

from pydantic import BaseModel


class AnswerReference(BaseModel):
    doc_name: str
    page_num: int
    sample_text: str


SearchReference = AnswerReference


class CrawlStatus(Enum):
    RUNNING = 1
    SUCCEEDED = 2
    FAILED = 3


IngestStatus = CrawlStatus
