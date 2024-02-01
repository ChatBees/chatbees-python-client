import json
from enum import Enum
from typing import List, Optional, Tuple, Dict

from pydantic import BaseModel

from chatbees.server_models.collection_api import CollectionBaseRequest


class AddDocRequest(CollectionBaseRequest):
    @classmethod
    def validate_to_json(cls, value):
        return cls(**json.loads(value)) if isinstance(value, str) else value

    def to_json_string(self) -> str:
        # fastapi server expects "property name enclosed in double quotes" when
        # using with UploadFile. pydantic.model_dump_json() uses single quote.
        # explicitly uses json.dumps for AddDocRequest.
        return json.dumps(self.__dict__)


class DeleteDocRequest(CollectionBaseRequest):
    doc_name: str


class ListDocsRequest(CollectionBaseRequest):
    pass


class ListDocsResponse(BaseModel):
    doc_names: List[str]


class AskRequest(CollectionBaseRequest):
    question: str
    top_k: Optional[int] = 5
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None


class AnswerReference(BaseModel):
    doc_name: str
    page_num: int
    sample_text: str


class AskResponse(BaseModel):
    answer: str
    refs: List[AnswerReference]


class SummaryRequest(CollectionBaseRequest):
    doc_name: str


class SummaryResponse(BaseModel):
    summary: str


class CreateCrawlRequest(CollectionBaseRequest):
    root_url: str
    max_urls_to_crawl: int = 200


class CreateCrawlResponse(BaseModel):
    crawl_id: str


class GetCrawlRequest(CollectionBaseRequest):
    crawl_id: str


class CrawlStatus(Enum):
    RUNNING = 1
    SUCCEEDED = 2
    FAILED = 3


class PageStats(BaseModel):
    char_count: int
    error_code: Optional[str] = None
    error_msg: Optional[str] = None


class GetCrawlResponse(BaseModel):
    root_url: str
    created_on: int
    max_pages: int
    crawl_status: CrawlStatus
    crawl_result: Optional[Dict[str, PageStats]] = None


class IndexCrawlRequest(CollectionBaseRequest):
    crawl_id: str
