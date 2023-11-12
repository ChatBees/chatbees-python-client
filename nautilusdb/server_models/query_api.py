from typing import List

from pydantic import BaseModel

from nautilusdb.server_models.search_api import VectorResult, Query


class QueryRequest(BaseModel):
    collection_name: str
    queries: List[Query]


class QueryResponse(BaseModel):
    # Return a list of search results.
    # In the future, query may include similarity scores
    results: List[VectorResult]