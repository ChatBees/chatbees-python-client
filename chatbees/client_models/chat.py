from typing import Optional, List, Tuple

from pydantic import BaseModel

from chatbees.server_models.doc_api import AskResponse
from chatbees.utils.ask import ask
from chatbees.utils.config import Config

__all__ = ["Chat"]


class Chat(BaseModel):
    """
    A new chatbot instance that supports conversational Q and A.
    """
    namespace_name: str
    collection_name: str
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None
    conversation_id: Optional[str] = None

    def ask(self, question: str, top_k: int = 5) -> AskResponse:
        resp = ask(
            Config.namespace,
            self.collection_name,
            question,
            top_k,
            doc_name=self.doc_name,
            history_messages=self.history_messages,
            conversation_id=self.conversation_id,
        )
        if self.history_messages is None:
            self.history_messages = []
        self.history_messages.append((question, resp.answer))
        if self.conversation_id is None:
            self.conversation_id = resp.conversation_id
        return resp
