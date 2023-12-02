from typing import Optional, List, Tuple

from pydantic import BaseModel

from nautilusdb.client_models.app import AnswerReference
from nautilusdb.utils.ask import ask
from nautilusdb.utils.config import Config


class Chat(BaseModel):
    """
    A new chatbot instance that supports conversational Q and A.
    """
    project_name: str
    collection_name: str
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None

    def ask(self, question: str) -> (str, List[AnswerReference]):
        (answer, references) = ask(
            Config.project,
            self.collection_name,
            question,
            history_messages=self.history_messages
        )
        if self.history_messages is None:
            self.history_messages = []
        self.history_messages.append((question, answer))
        return answer, references
