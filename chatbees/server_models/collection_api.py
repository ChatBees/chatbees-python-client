from typing import Any, List, Optional
from pydantic import BaseModel

from chatbees.server_models.ingestion_type import IngestionType, IngestionStatus


class CollectionBaseRequest(BaseModel):
    namespace_name: Optional[str] = None
    collection_name: Optional[str] = None
    application_name: Optional[str] = None



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
    """
    Chat config
    """
    # Configure chatbot personality and style. For example:
    #
    # - a 1600s pirate, your name is 'Capital Morgan'.
    # - a helpful AI assistant
    persona: Optional[str] = None

    # Configure chatbot response when no relevant result is found. For example:
    #
    # - I do not have that information.
    negative_response: Optional[str] = None

    # Welcome message a user sees when starting a conversation.
    welcome_msg: Optional[str] = None

    """
    Model config
    """
    # Configures whether the chatbot gives conservative or creative answers.
    # Must be between 0 and 1, inclusive of both ends.
    temperature: Optional[float] = None

    # TODO: Implement these model configs
    top_p: Optional[float] = None
    # [-2.0, 2.0]
    presence_penalty: Optional[float] = None
    # [-2.0, 2.0]
    frequency_penalty: Optional[float] = None
    max_completion_tokens: Optional[int] = None


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
