from typing import Any, List

from pydantic import BaseModel

from chatbees.server_models.collection_api import CollectionBaseRequest
from chatbees.server_models.ingestion_type import IngestionType, IngestionStatus

"""
When ingesting data from a data source, please create a connector (e.g., connect
a data source via the ChatBees UI). The connection will go through the OAuth
mechanism of the data source. Each connector has a unique connector ID, which is
used for the ingestion process.
"""

class ConnectorReference(BaseModel):
    id: str
    type: IngestionType
    name: str

class ListConnectorsRequest(BaseModel):
    pass

class ListConnectorsResponse(BaseModel):
    connectors: List[ConnectorReference]


class CreateIngestionRequest(CollectionBaseRequest):
    connector_id: str
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
