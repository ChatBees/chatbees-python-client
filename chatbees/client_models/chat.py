from typing import Optional, List, Tuple

from pydantic import BaseModel

from chatbees.server_models.doc_api import AskResponse
from chatbees.utils.ask import ask, ask_application
from chatbees.utils.config import Config

__all__ = ["Chat"]


class Chat(BaseModel):
    """
    A new chatbot instance that supports conversational Q and A.
    """
    namespace_name: Optional[str] = None
    collection_name: Optional[str] = None
    application_name: Optional[str] = None
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None
    conversation_id: Optional[str] = None

    def _validate_names(self):
        if self.application_name is not None and self.namespace_name is None and self.collection_name is None:
            return
        if self.application_name is None and self.namespace_name is not None and self.collection_name is not None:
            return
        raise ValueError(f"Chat must specify either both namespace and collection, or application")

    def ask(self, question: str, top_k: int = 5) -> AskResponse:
        self._validate_names()

        if self.application_name is None:
            resp = ask(
                Config.namespace,
                self.collection_name,
                question,
                top_k,
                doc_name=self.doc_name,
                history_messages=self.history_messages,
                conversation_id=self.conversation_id,
            )
        else:
            resp = ask_application(
                self.application_name,
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
