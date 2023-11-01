import os
from typing import List, Dict
from urllib import request

from pydantic import BaseModel

from nautilusdb.client_models.column_type import ColumnType
from nautilusdb.client_models.app import AnswerReference
from nautilusdb.server_models.app_api import AddDocRequest, AskRequest, AskResponse
from nautilusdb.utils.config import Config
from nautilusdb.utils.exceptions import Unimplemented
from nautilusdb.client_models.vector import Vector
from nautilusdb.server_models.api import UpsertRequest, UpsertResponse
from nautilusdb.utils.file_upload import (
    is_url,
    validate_file,
    validate_url_file,
)

__all__ = ["Collection"]


class Collection(BaseModel):
    """
    A Collection is a named vector search index with a fixed embedding dimension.

    Usage:
        import nautilusdb as ndb
        collection =  ndb.create_collection(ndb.
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
    metadata_columns: Dict[str, ColumnType] = {}

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
            collection_name=self.name,
            vectors=[v.to_api_vector() for v in vectors])
        resp = Config.post(url=url, data=req.model_dump_json())
        resp = UpsertResponse.model_validate(resp.json())
        return resp.upsert_count

    def delete_vector(self, vector_ids=List[str]):
        """
        Deletes vectors specified by the given list of vector IDs from the
        collection.

        :param vector_ids: IDs of vectors to delete
        :return:
        """
        raise Unimplemented("delete_vector is not yet implemented")

    def upload_document(self, path_or_url: str):
        """
        Uploads a local or web document into this collection.

        :param path_or_url: Local file path or the URL of a document. URL must
                            contain scheme (http or https) prefix.
        :return:
        """
        url = f'{Config.get_base_url()}/qadocs/add'
        req = AddDocRequest(collection_name=self.name)
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
        url = f'{Config.get_base_url()}/qadocs/ask'
        req = AskRequest(collection_name=self.name, question=question)

        resp = Config.post(url=url, data=req.model_dump_json())
        resp = AskResponse.model_validate(resp.json())

        unique_doc_names = {ref.doc_name for ref in resp.refs}

        return (
            resp.answer,
            [AnswerReference(doc_name=name) for name in unique_doc_names]
        )
