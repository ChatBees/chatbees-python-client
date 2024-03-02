from typing import Optional, List

from pydantic import BaseModel

from chatbees.server_models.doc_api import SearchReference
from chatbees.server_models.collection_api import CollectionBaseRequest


class SearchRequest(CollectionBaseRequest):
    question: str
    top_k: Optional[int] = 10

class SearchResponse(BaseModel):
    refs: List[SearchReference]
