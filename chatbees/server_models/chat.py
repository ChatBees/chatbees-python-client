from typing import Optional

from pydantic import BaseModel

from chatbees.server_models.collection_api import CollectionBaseRequest, ChatAttributes


class ConfigureChatRequest(CollectionBaseRequest):
    """
    Configures a collection with custom q/a attributes
    """
    chat_attributes: ChatAttributes
