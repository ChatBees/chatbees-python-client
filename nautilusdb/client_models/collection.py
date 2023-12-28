import os
from typing import List, Dict, Optional
from urllib import request

from pydantic import BaseModel

from nautilusdb.client_models.chat import Chat
from nautilusdb.client_models.doc import AnswerReference
from nautilusdb.server_models.doc_api import (
    AddDocRequest,
    AskRequest,
    AskResponse,
    SummaryRequest,
    SummaryResponse,
)
from nautilusdb.server_models.collection_api import (
    DescribeCollectionResponse,
)
from nautilusdb.utils.ask import ask
from nautilusdb.utils.config import Config
from nautilusdb.utils.file_upload import (
    is_url,
    validate_file,
    validate_url_file,
)

__all__ = ["Collection"]


class Collection(BaseModel):
    """
    A Collection stores a list of documents and supports chatting with
    the documents.
    """
    #  Name of the collection
    name: str

    # Description of the collection
    description: str = ""

    def upload_document(self, path_or_url: str):
        """
        Uploads a local or web document into this collection.

        :param path_or_url: Local file path or the URL of a document. URL must
                            contain scheme (http or https) prefix.
        :return:
        """
        url = f'{Config.get_base_url()}/docs/add'
        req = AddDocRequest(namespace_name=Config.namespace,
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
        url = f'{Config.get_base_url()}/docs/summary'
        req = SummaryRequest(
            namespace_name=Config.namespace,
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
        return ask(Config.namespace, self.name, question)

    def chat(self, doc_name=None) -> Chat:
        """
        Creates a new chatbot within the collection.

        :param doc_name: If specified, chatbot is scoped to the given document only
        :return: A new Chat object
        """
        return Chat(
            namespace_name=Config.namespace,
            collection_name=self.name,
            doc_name=doc_name
        )

def describe_response_to_collection(
    collection_name: str,
    resp: DescribeCollectionResponse
) -> Collection:
    description = ""
    if resp.description is not None:
        description = resp.description
    return Collection(
        name=collection_name,
        description=description,
    )
