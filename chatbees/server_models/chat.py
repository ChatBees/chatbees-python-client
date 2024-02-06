from typing import Optional

from pydantic import BaseModel

from chatbees.server_models.collection_api import CollectionBaseRequest


class ChatAttributes(BaseModel):
    # Configure chatbot personality and style. For example:
    #
    # - a 1600s pirate, your name is 'Capitan Morgan'.
    # - a helpful AI assistant
    persona: Optional[str] = None

    # Configure chatbot response when no relevant result is found. For example:
    #
    # - I do not have that information.
    negative_response: Optional[str] = None


class ConfigureChatRequest(CollectionBaseRequest):
    """
    Configures a collection with custom q/a attributes
    """
    chat_attributes: ChatAttributes