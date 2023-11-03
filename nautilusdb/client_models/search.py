from typing import List, Optional

from pydantic import BaseModel

from nautilusdb.client_models.vector import VectorResult


__all__ = ["SearchRequest", "SearchResponse"]


class SearchRequest(BaseModel):
    """
    A query against a collection.
    """

    # Embedding of the query
    embedding: List[float]

    """
    SQL-compatible Metadata filter. Filter operations can be performed on any
    metadata column declared in the collection of supported data type.
    
    Supported data types: Boolean, Int, Long , Float, Double, String
    
    Supported filter operators (a subset of SQL:1999 standard)
    - Arithmetic Operators: + , - , * , / , %
    - Comparison Operators: =, <, >, <=, >=, !=
    - Boolean Operators: and, or, not
    - Grouping Operators: ()
    - Null Check: is null, is not null
    
    Note about filter syntax:
    - Do not enclose metadata column names
    - Do not enclose Int, Long, Float or Double values.
    - Enclose String values with single quote
   
    Examples:
    1. A Collection contains 'published_on (int)' metadata column that contains
       the epoch timestamp of when a vector is published. 'tag (string)' column 
       that contains a tag for the vector. The following filter can be used to
       restricts query results to only important vectors published after 
       1/1/2022 GMT.
    
       published_on > 1641024000 and tag = 'important'
       
    2. A Collection contains reddit comments with metadata columns 'karma (int)'
       . 'published_on (int)', 'char_count (int)'. The following could be a 
       reasonable filter to restrict results to only recent, popular and 
       informative comments.
       
       karma >= 50 and published_on > 1641024000  and char_count > 100
       
    3. Other examples of valid filters
       (foo_int > 10 or bar_string = 'front_page') and baz_string != 'draft'
       (a = 1 or (b = 2 and c = 3 and (d = 4 or e = 5)))
    """
    metadata_filter: Optional[str] = None

    # A list of metadata columns to return with the vector embedding
    include_metadata: Optional[List[str]] = None

    # Whether embeddings are returned
    include_values: Optional[bool] = False

    # Number of results to return
    top_k: Optional[int] = 3


class SearchResponse(BaseModel):
    """
    Result of a query
    """
    vectors: List[VectorResult]
