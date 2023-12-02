from typing import List

from pydantic import BaseModel

from nautilusdb.server_models.collection_api import CollectionBaseRequest
from nautilusdb.server_models.search_api import VectorResult, Query


class QueryRequest(CollectionBaseRequest):
    queries: List[Query]


class QueryResponse(BaseModel):
    # Return a list of search results.
    # In the future, query may include similarity scores
    results: List[VectorResult]