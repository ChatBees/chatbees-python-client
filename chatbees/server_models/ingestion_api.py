from typing import Any

from pydantic import BaseModel

from chatbees.server_models.doc_api import CrawlStatus
from chatbees.server_models.collection_api import CollectionBaseRequest
from chatbees.server_models.ingestion_type import CrawlType


class CreateIngestionRequest(CollectionBaseRequest):
    type: CrawlType
    spec: Any


class CreateIngestionResponse(BaseModel):
    ingestion_id: str


class GetIngestionRequest(CollectionBaseRequest):
    ingestion_id: str


class GetIngestionResponse(BaseModel):
    ingestion_id: str
    ingestion_status: CrawlStatus


class IndexIngestionRequest(CollectionBaseRequest):
    ingestion_id: str

