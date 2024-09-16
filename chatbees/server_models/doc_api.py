import json
from enum import Enum
from typing import List, Optional, Tuple, Dict

from pydantic import BaseModel

from chatbees.server_models.collection_api import CollectionBaseRequest
from chatbees.server_models.ingestion_type import IngestionStatus, ScheduleSpec

__all__ = [
    "AnswerReference",
    "SearchReference",
    "CrawlStatus",
    "PageStats",
]

class AddDocRequest(CollectionBaseRequest):
    # fastapi server expects "property name enclosed in double quotes" when
    # using with UploadFile. pydantic.model_dump_json() uses single quote.
    # explicitly uses json.loads() and dumps().
    @classmethod
    def validate_to_json(cls, value):
        return cls(**json.loads(value)) if isinstance(value, str) else value

    def to_json_string(self) -> str:
        return json.dumps(self.__dict__)


class DeleteDocRequest(CollectionBaseRequest):
    doc_name: str


class ListDocsRequest(CollectionBaseRequest):
    pass


class DocumentType(Enum):
    FILE = 'FILE'
    WEBSITE = 'WEBSITE'
    NOTION = 'NOTION'
    GDRIVE = 'GDRIVE'
    CONFLUENCE = 'CONFLUENCE'


class DocumentMetadata(BaseModel):
    name: str
    # URL that can be used to access this document.
    # If None, this document cannot be accessed via URL
    url: Optional[str] = None
    type: DocumentType


class ListDocsResponse(BaseModel):
    documents: List[DocumentMetadata] = []

    # To be deprecated
    doc_names: List[str]


class AskRequest(CollectionBaseRequest):
    question: str
    top_k: Optional[int] = 5
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None
    # this ask continues previous conversation. This is for the server to
    # associate the questions for feedback/analysis. The caller should pass
    # history_messages as context for the current question. This is much more
    # efficient than the server to load history messages.
    conversation_id: Optional[str] = None


class AnswerReference(BaseModel):
    doc_name: str
    page_num: int
    sample_text: str

SearchReference = AnswerReference


class AskResponse(BaseModel):
    answer: str
    refs: List[AnswerReference]

    # An ID to uniquely identify this interaction
    request_id: str

    # ID of the current conversation.
    # Set `conversation_id` in the next Ask request to continue this conversation.
    conversation_id: str


class SummaryRequest(CollectionBaseRequest):
    doc_name: str


class SummaryResponse(BaseModel):
    summary: str


class ExtractRelevantTextsRequest(CollectionBaseRequest):
    # find the texts relevant to the input texts in the doc
    doc_name: str
    input_texts: str

class ExtractRelevantTextsResponse(BaseModel):
    relevant_texts: str


class OutlineFAQRequest(CollectionBaseRequest):
    doc_name: str

class FAQ(BaseModel):
    question: str
    answer: str

class OutlineFAQResponse(BaseModel):
    outlines: list[str]
    faqs: list[FAQ]


class TranscribeAudioRequest(CollectionBaseRequest):
    lang: str

    # optional url to download the audio file from
    url: Optional[str] = None
    # optional access token to download the audio file from the url
    access_token: Optional[str] = None

    # fastapi server expects "property name enclosed in double quotes" when
    # using with UploadFile. pydantic.model_dump_json() uses single quote.
    # explicitly uses json.loads() and dumps().
    @classmethod
    def validate_to_json(cls, value):
        return cls(**json.loads(value)) if isinstance(value, str) else value

    def to_json_string(self) -> str:
        return json.dumps(self.__dict__)

class TranscribeAudioResponse(BaseModel):
    transcript: str


class CreateCrawlRequest(CollectionBaseRequest):
    root_url: str
    max_urls_to_crawl: int = 200
    # periodical crawl scheduling. run once if None.
    # Only support one schedule for one collection. If a collection crawls
    # multiple root_urls, can only specify schedule for one root_url. The old
    # schedule will be automatically overridden.
    schedule: Optional[ScheduleSpec] = None


class CreateCrawlResponse(BaseModel):
    crawl_id: str


# delete the index for the crawled pages of root_url
class DeleteCrawlRequest(CollectionBaseRequest):
    root_url: str


class DeleteCrawlResponse(BaseModel):
    pass


class GetCrawlRequest(CollectionBaseRequest):
    crawl_id: str


CrawlStatus = IngestionStatus

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
