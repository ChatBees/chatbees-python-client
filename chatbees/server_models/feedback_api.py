import re
import shortuuid
from enum import Enum
from pydantic import BaseModel, model_validator
from typing import Optional, List

from chatbees.server_models.collection_api import CollectionBaseRequest


class FeedbackSource(str, Enum):
    WEBSITE = 'WEBSITE'


class UnregisteredUser(BaseModel):
    source: FeedbackSource
    email: str = ''
    name: str = ''

    @model_validator(mode='after')
    def validate_input(self) -> 'UnregisteredUser':
        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
        if self.email != "" and not re.match(pattern, self.email):
            raise ValueError("Invalid email address")
        if len(self.email) > 140:
            raise ValueError("Email address too long")
        if len(self.name) > 140:
            raise ValueError("Name too long")
        return self


class CreateOrUpdateFeedbackRequest(CollectionBaseRequest):
    """
    Provides feedback for the answer or search results.
    """
    # the request id of the ask() or search()
    request_id: str
    thumb_down: bool = False
    text_feedback: str = ""

    # Contact information of non-logged-in user, such as customer email from
    # the website chatbot, slackbot user, etc.
    unregistered_user: Optional[UnregisteredUser] = None

    @model_validator(mode='after')
    def validate_input(self) -> 'CreateOrUpdateFeedbackRequest':
        try:
            shortuuid.decode(self.request_id)
        except Exception:
            raise ValueError("Invalid request id")

        if len(self.text_feedback) > 1_000:
            raise ValueError("Text feedback is limited to 1000 characters")
        return self
