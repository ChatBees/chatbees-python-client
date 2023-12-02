import os
from typing import List, Dict, Optional
from urllib import request

from pydantic import BaseModel

from nautilusdb.client_models.chat import Chat
from nautilusdb.client_models.column_type import ColumnType
from nautilusdb.client_models.app import AnswerReference
from nautilusdb.client_models.query import QueryRequest, VectorResponse
from nautilusdb.client_models.search import SearchRequest
from nautilusdb.server_models.app_api import (
    AddDocRequest,
    AskRequest,
    AskResponse,
    SummaryRequest,
    SummaryResponse,
)
from nautilusdb.server_models.collection_api import (
    DeleteVectorsRequest,
    DescribeCollectionResponse,
)
from nautilusdb.server_models.search_api import (
    SearchWithEmbedding,
    Query,
    SearchRequest as ServerSearchRequest,
    SearchResponse as ServerSearchResponse,
)
from nautilusdb.server_models.query_api import (
    QueryRequest as ServerQueryRequest,
    QueryResponse as ServerQueryResponse,
)
from nautilusdb.utils.ask import ask
from nautilusdb.utils.config import Config
from nautilusdb.client_models.vector import Vector
from nautilusdb.server_models.vector_api import (
    Vector as ServerVector,
    UpsertRequest,
    UpsertResponse,
)
from nautilusdb.utils.file_upload import (
    is_url,
    validate_file,
    validate_url_file,
)

__all__ = ["Collection"]


class Collection(BaseModel):
    """
    A Collection is a named vector search index with a fixed embedding dimension.
    """
    #  Name of the collection
    name: str

    # Dimension of the vectors in this collection
    dimension: int = 0

    # Description of the collection
    description: str = ""

    # A set of metadata columns associated with vectors in this collection.
    #       Key: Column name
    #       Value: Column type(avro primitive type)
    metadata_columns: Optional[Dict[str, ColumnType]] = None

    # Distance metric used for vector search.
    # Only 'l2' distance is supported.
    distance_metric: str = 'l2'

    def upsert_vector(self, vectors: List[Vector]) -> int:
        """
        Upserts a list of vectors.

        For every vector in the list:
        - If a vector with the same ID already exists in the collection,
          it will be replaced with the provided vector
        - If a vector with the same ID does not exist in the collection, the
          provided vector will be created.

        :param vectors: A list of vectors to create or update
        :return: The number of vectors created or updated
        """
        url = f'{Config.get_base_url()}/vectors/upsert'
        req = UpsertRequest(
            project_name=Config.project,
            collection_name=self.name,
            vectors=[ServerVector.from_client_vector(v) for v in vectors])
        resp = Config.post(url=url, data=req.model_dump_json())
        resp = UpsertResponse.model_validate(resp.json())
        return resp.upsert_count

    def delete_vectors(
        self,
        vector_ids: List[str] = None,
        metadata_filter: str = None,
        delete_all=False
    ):
        """
        Deletes vectors specified by the given list of vector IDs from the
        collection. Exactly one of `vector_ids`, `metadata_filter`, `delete_all`
        must be specified.

        `metadata_filter` is A SQL-compatible filter to specify vector deletion
        condition. For example, "foo_col > 1" indicates all vectors where the
        value of metadata column 'foo_col' greater than 1 should be deleted.

        All columns referenced in `metadata_filter` must exist in the
        collection, you can retrieve the list of columns via describe_collection
        API `ndb.describe_collection(<collection_name>)`.

        Simplified metadata filter syntax (EBNF grammar will be published soon):

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
        1. Deletes all vectors tagged with "draft" that were created before
           1/1/2022.

           created_on < 1641024000 and tag = 'draft'

        2. A Collection contains reddit comments with metadata columns
           'karma (int)', 'published_on (int)', 'char_count (int)'.
           The following could be a filter to remove all unpopular or very short
           comments.

           karma >= 50 or char_count > 10

        3. Other examples of valid filters
           (foo_int > 10 or bar_string = 'front_page') and baz_string != 'draft'
           (a = 1 or (b = 2 and c = 3 and (d = 4 or e = 5)))

        :param collection_name: name of the collection
        :param vector_ids: IDs of vectors to delete
        :param metadata_filter: A SQL-compatible filter to specify vector
                                deletion condition. For example, "foo_col > 1"
                                indicates all vectors where the value of
                                metadata column 'foo_col' greater than 1 should
                                be deleted.
        :param delete_all: Delete all vectors
        """
        specified_fields = (int(vector_ids is not None) +
                            int(metadata_filter is not None) +
                            int(delete_all))
        if specified_fields != 1:
            raise ValueError(
                "Exactly one of `vector_ids`, `metadata_filter` "
                "and `delete_all` must be specified")
        req = DeleteVectorsRequest(
            project_name=Config.project,
            collection_name=self.name,
            vector_ids=vector_ids,
            where=metadata_filter,
            delete_all=delete_all)
        url = f'{Config.get_base_url()}/vectors/delete'
        Config.post(url=url, data=req.model_dump_json())

    def upload_document(self, path_or_url: str):
        """
        Uploads a local or web document into this collection.

        :param path_or_url: Local file path or the URL of a document. URL must
                            contain scheme (http or https) prefix.
        :return:
        """
        url = f'{Config.get_base_url()}/qadocs/add'
        req = AddDocRequest(project_name=Config.project,
                            collection_name=self.name)
        if is_url(path_or_url):
            validate_url_file(path_or_url)
            with request.urlopen(path_or_url) as f:
                fname = os.path.basename(path_or_url)
                Config.post(
                    url=url, files={'file': (fname, f)},
                    data={'request': req.model_dump_json()})
        else:
            # Handle tilde "~/blah"
            path_or_url = os.path.expanduser(path_or_url)
            validate_file(path_or_url)
            with open(path_or_url, 'rb') as f:
                fname = os.path.basename(path_or_url)
                Config.post(
                    url=url, files={'file': (fname, f)},
                    data={'request': req.model_dump_json()})

    def summarize_document(self, doc_name) -> str:
        """
        Returns a summary of the document.

        :param path_or_url: Local path or url to the uploaded document
        :return: A summary of the document
        """
        url = f'{Config.get_base_url()}/qadocs/summary'
        req = SummaryRequest(
            project_name=Config.project,
            collection_name=self.name,
            doc_name=doc_name,
        )
        resp = Config.post(url=url, data=req.model_dump_json())
        resp = SummaryResponse.model_validate(resp.json())
        return resp.summary

    def ask(
        self,
        question: str,
    ) -> (str, List[AnswerReference]):
        """
        Ask a question within the context of this collection.

        :param question: Question in plain text.
        :return: A tuple
            - answer: A plain-text answer to the given question
            - references: A list of most relevant document references in the
                          collection
        """
        return ask(Config.project, self.name, question)

    def search(self, queries: List[SearchRequest]) -> List[VectorResponse]:
        """
        Searches the collection
        """
        req = ServerSearchRequest(
            project_name=Config.project,
            collection_name=self.name,
            queries=[
                SearchWithEmbedding.from_client_request(q) for q in queries])

        url = f'{Config.get_base_url()}/vectors/search'

        resp = Config.post(url=url, data=req.model_dump_json())
        resp = ServerSearchResponse.model_validate(resp.json())
        return [r.to_client_response() for r in resp.results]

    def query(self, queries: List[QueryRequest]) -> List[VectorResponse]:
        """
        Queries the collection
        """
        req = ServerQueryRequest(
            project_name=Config.project,
            collection_name=self.name,
            queries=[
                Query.from_client_request(q) for q in queries])

        url = f'{Config.get_base_url()}/vectors/query'

        resp = Config.post(url=url, data=req.model_dump_json())
        resp = ServerQueryResponse.model_validate(resp.json())
        return [r.to_client_response() for r in resp.results]

    def chat(self, doc_name=None) -> Chat:
        """
        Creates a new chatbot within the collection.

        :param doc_name: If specified, chatbot is scoped to the given document only
        :return: A new Chat object
        """
        return Chat(
            project_name=Config.project,
            collection_name=self.name,
            doc_name=doc_name
        )

def describe_response_to_collection(
    resp: DescribeCollectionResponse
) -> Collection:
    return Collection(
        name=resp.collection_name,
        dimension=resp.dimension,
        metadata_columns=resp.metas,
    )
