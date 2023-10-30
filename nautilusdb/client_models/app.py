__all__ = ["AnswerReference"]

from pydantic import BaseModel


class AnswerReference(BaseModel):
    doc_name: str
