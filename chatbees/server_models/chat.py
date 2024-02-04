from typing import Optional

from pydantic import BaseModel


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

    # Configures whether the chatbot gives conservative or creative answers.
    # Must be between 0 and 1, inclusive of both ends.
    temperature: Optional[float] = None