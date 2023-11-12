from typing import List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.query import QueryRequestBase


__all__ = ["SearchRequest"]


class SearchRequest(QueryRequestBase):
    """
    A search against a collection.
    """
    # Embedding of the query
    embedding: List[float]
