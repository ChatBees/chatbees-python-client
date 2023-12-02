import json
from typing import List, Optional, Tuple

from pydantic import BaseModel

from nautilusdb.server_models.collection_api import CollectionBaseRequest


class AddDocRequest(CollectionBaseRequest):
    @classmethod
    def validate_to_json(cls, value):
        return cls(**json.loads(value)) if isinstance(value, str) else value

    def to_json_string(self) -> str:
        # fastapi server expects "property name enclosed in double quotes" when
        # using with UploadFile. pydantic.model_dump_json() uses single quote.
        # explicitly uses json.dumps for AddDocRequest.
        return json.dumps(self.__dict__)


class AskRequest(CollectionBaseRequest):
    question: str
    top_k: Optional[int] = 5
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None


class AnswerReference(BaseModel):
    doc_name: str


class AskResponse(BaseModel):
    answer: str
    refs: List[AnswerReference]


class SummaryRequest(CollectionBaseRequest):
    doc_name: str


class SummaryResponse(BaseModel):
    summary: str
