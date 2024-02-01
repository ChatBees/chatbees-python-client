from typing import Optional, List, Tuple

from pydantic import BaseModel

from chatbees.client_models.doc import AnswerReference
from chatbees.utils.ask import ask
from chatbees.utils.config import Config


class Chat(BaseModel):
    """
    A new chatbot instance that supports conversational Q and A.
    """
    namespace_name: str
    collection_name: str
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None

    def ask(self, question: str, top_k: int = 5) -> (str, List[AnswerReference]):
        (answer, references) = ask(
            Config.namespace,
            self.collection_name,
            question,
            top_k,
            doc_name=self.doc_name,
            history_messages=self.history_messages,
        )
        if self.history_messages is None:
            self.history_messages = []
        self.history_messages.append((question, answer))
        return answer, references
