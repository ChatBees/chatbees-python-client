from typing import Any

from pydantic import BaseModel

from chatbees.server_models.doc_api import IngestionStatus
from chatbees.server_models.collection_api import CollectionBaseRequest
from chatbees.server_models.ingestion_type import IngestionType


class CreateIngestionRequest(CollectionBaseRequest):
    type: IngestionType
    spec: Any


class CreateIngestionResponse(BaseModel):
    ingestion_id: str


class GetIngestionRequest(CollectionBaseRequest):
    ingestion_id: str


class GetIngestionResponse(BaseModel):
    ingestion_status: IngestionStatus


class IndexIngestionRequest(CollectionBaseRequest):
    ingestion_id: str

