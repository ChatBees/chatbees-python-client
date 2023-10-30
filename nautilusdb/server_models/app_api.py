import json
from typing import List

from pydantic import BaseModel


class AddDocRequest(BaseModel):
    collection_name: str

    @classmethod
    def validate_to_json(cls, value):
        return cls(**json.loads(value)) if isinstance(value, str) else value

    def to_json_string(self) -> str:
        # fastapi server expects "property name enclosed in double quotes" when
        # using with UploadFile. pydantic.model_dump_json() uses single quote.
        # explicitly uses json.dumps for AddDocRequest.
        return json.dumps(self.__dict__)


class AskRequest(BaseModel):
    collection_name: str
    question: str


class AnswerReference(BaseModel):
    doc_name: str


class AskResponse(BaseModel):
    answer: str
    refs: List[AnswerReference]