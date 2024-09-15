from typing import Any, List, Optional
from pydantic import BaseModel

from chatbees.server_models.ingestion_type import IngestionType, IngestionStatus


class CollectionBaseRequest(BaseModel):
    namespace_name: str
    collection_name: str


class CreateCollectionRequest(CollectionBaseRequest):
    description: Optional[str] = None

    # If true, create a collection that can be read without an API key
    public_read: Optional[bool] = None


class ConfigureCollectionRequest(CollectionBaseRequest):
    description: Optional[str] = None
    # whether the collection is publicly readable
    public_read: Optional[bool] = None


class DeleteCollectionRequest(CollectionBaseRequest):
    pass


class ListCollectionsRequest(BaseModel):
    namespace_name: str


class ListCollectionsResponse(BaseModel):
    names: List[str]


class ChatAttributes(BaseModel):
    # Configure chatbot role, personality and style. For example:
    #
    # - You are an AI assistant. You will talk like a 1600s pirate.
    # - You are an AI assistant.
    # - You are an AI customer support agent.
    persona: Optional[str] = None

    # Configure chatbot response when no relevant result is found. For example:
    #
    # - I do not have that information.
    negative_response: Optional[str] = None


class PeriodicIngest(BaseModel):
    type: IngestionType
    # the crawl spec
    spec: Any
    # the last ingestion epoch time
    last_ingest_time: int
    last_ingest_status: IngestionStatus


class DescribeCollectionRequest(CollectionBaseRequest):
    pass


class DescribeCollectionResponse(BaseModel):
    description: Optional[str] = None

    # Chat attributes configured for this collection, if any
    chat_attributes: Optional[ChatAttributes] = None

    # If true, the collection can be read without an API key
    public_read: Optional[bool] = None

    # ingestins that run periodically for the collection
    periodic_ingests: Optional[List[PeriodicIngest]] = None
