from typing import Any

from pydantic import BaseModel

from chatbees.server_models.collection_api import CollectionBaseRequest
from chatbees.server_models.ingestion_type import IngestionType, IngestionStatus


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


class DeleteIngestionRequest(CollectionBaseRequest):
    type: IngestionType


class UpdatePeriodicIngestionRequest(CollectionBaseRequest):
    type: IngestionType
    spec: Any


class DeletePeriodicIngestionRequest(CollectionBaseRequest):
    type: IngestionType
