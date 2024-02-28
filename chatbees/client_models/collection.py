import os
from typing import List, Dict, Tuple, Optional
from urllib import request

from pydantic import BaseModel

from chatbees.client_models.chat import Chat
from chatbees.client_models.doc import AnswerReference, CrawlStatus, IngestStatus
from chatbees.server_models.chat import ConfigureChatRequest, ChatAttributes
from chatbees.server_models.crawl_type import WebsiteSpec, IngestType, NotionSpec, ConfluenceSpec
from chatbees.server_models.doc_api import (
    AddDocRequest,
    DeleteDocRequest,
    ListDocsRequest,
    ListDocsResponse,
    SummaryRequest,
    SummaryResponse,
    CreateCrawlRequest,
    CreateCrawlResponse,
    GetCrawlRequest,
    GetCrawlResponse,
    PageStats,
    IndexCrawlRequest,
    DeleteCrawlRequest,
)
from chatbees.server_models.collection_api import (
    DescribeCollectionResponse,
)
from chatbees.server_models.ingestion_api import (
    CreateIngestionRequest,
    CreateIngestionResponse,
    GetIngestionRequest, GetIngestionResponse, IndexIngestionRequest,
)
from chatbees.utils.ask import ask
from chatbees.utils.config import Config
from chatbees.utils.file_upload import (
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

    # If true, collection can be read without an API key
    public_read: bool = False

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

    def delete_document(self, doc_name: str):
        """
        Deletes the document.

        :param doc_name: the document to delete
        """
        url = f'{Config.get_base_url()}/docs/delete'
        req = DeleteDocRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            doc_name=doc_name,
        )
        Config.post(url=url, data=req.model_dump_json())

    def list_documents(self) -> List[str]:
        """
        List the documents.

        :return: A list of the documents
        """
        url = f'{Config.get_base_url()}/docs/list'
        req = ListDocsRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
        )
        resp = Config.post(url=url, data=req.model_dump_json())
        list_resp = ListDocsResponse.model_validate(resp.json())
        return list_resp.doc_names

    def summarize_document(self, doc_name: str) -> str:
        """
        Returns a summary of the document.

        :param doc_name: the document to summarize
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
        self, question: str, top_k: int = 5, doc_name: str = None,
    ) -> (str, List[AnswerReference]):
        """
        Ask a question within the context of this collection.

        :param question: Question in plain text.
        :param top_k: the top k relevant contexts to get answer from.
        :param doc_name: if specified, ask is scoped to the given document only.
        :return: A tuple
            - answer: A plain-text answer to the given question
            - references: A list of most relevant document references in the
                          collection
        """
        return ask(Config.namespace, self.name, question, top_k, doc_name)

    def chat(self, doc_name: str = None) -> Chat:
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

    # deprecated. Please use create_website_ingestion function
    def create_crawl(self, root_url: str, max_urls_to_crawl: int) -> str:
        """
        Create a crawl task to crawl the root_url.

        :param root_url: the root url to carwl
        :param max_urls_to_crawl: the max number of urls to crawl
        :return: the id of the crawl
        """
        url = f'{Config.get_base_url()}/docs/create_crawl'
        req = CreateCrawlRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            root_url=root_url,
            max_urls_to_crawl=max_urls_to_crawl,
        )
        resp = Config.post(url=url, data=req.model_dump_json())
        crawl_resp = CreateCrawlResponse.model_validate(resp.json())
        return crawl_resp.crawl_id

    def _create_ingestion(self, ingestion_type, ingestion_spec) -> str:
        url = f'{Config.get_base_url()}/docs/create_ingestion'
        req = CreateIngestionRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            type=ingestion_type,
            spec=ingestion_spec)
        resp = Config.post(url=url, data=req.model_dump_json())
        ingest_resp = CreateIngestionResponse.model_validate(resp.json())
        return ingest_resp.ingestion_id

    def create_website_ingestion(self, root_url: str, max_urls_to_crawl) -> str:
        """
        Create an Ingestion task to crawl the root_url.

        :param root_url: the root url to crawl
        :param max_urls_to_crawl: the max number of urls to crawl
        :return: the id of the ingestion
        """
        spec = WebsiteSpec(root_url=root_url, max_urls_to_crawl=max_urls_to_crawl)
        return self._create_ingestion(IngestType.WEBSITE, spec)

    def create_notion_ingestion(self, token: str) -> str:
        """
        Create an Ingestion task to crawl Notion

        :param token: the authorization token returned by Notion oauth
        :return: the id of the ingestion
        """
        spec = NotionSpec(token=token)
        return self._create_ingestion(IngestType.NOTION, spec)

    def create_confluence_ingestion(
        self,
        token: str,
        url: str,
        space: str,
        user_name: Optional[str] = None
    ) -> str:
        spec = ConfluenceSpec(
            token=token, url=url, space=space, user_name=user_name)
        return self._create_ingestion(IngestType.CONFLUENCE, spec)

    def get_ingestion(self, ingestion_id: str) -> IngestStatus:
        url = f'{Config.get_base_url()}/docs/get_ingestion'
        req = GetIngestionRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            ingestion_id=ingestion_id)
        resp = Config.post(url=url, data=req.model_dump_json())
        get_resp = GetIngestionResponse.model_validate(resp.json())
        return get_resp.ingestion_status

    def index_ingestion(self, ingestion_id: str):
        url = f'{Config.get_base_url()}/docs/index_ingestion'
        req = IndexIngestionRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            ingestion_id=ingestion_id)
        Config.post(url=url, data=req.model_dump_json())

    # deprecated. Please use get_ingestion function
    def get_crawl(
        self, crawl_id: str,
    ) -> Tuple[CrawlStatus, Dict[str, PageStats]]:
        """
        Create a crawl task to crawl the root_url.

        :param crawl_id: the id of the crawl
        :return: A tuple
            - crawl status: the status of crawl
            - page stats: A dict of page urls and stats
        """
        url = f'{Config.get_base_url()}/docs/get_crawl'
        req = GetCrawlRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            crawl_id=crawl_id,
        )
        resp = Config.post(url=url, data=req.model_dump_json())
        crawl_resp = GetCrawlResponse.model_validate(resp.json())
        return crawl_resp.crawl_status, crawl_resp.crawl_result

    # deprecated. Please use index_ingestion function
    def index_crawl(self, crawl_id: str):

        """
        Index the crawled pages.

        :param crawl_id: the id of the crawl
        """
        url = f'{Config.get_base_url()}/docs/index_crawl'
        req = IndexCrawlRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            crawl_id=crawl_id,
        )
        Config.post(url=url, data=req.model_dump_json())

    def delete_crawl(self, root_url: str):
        """
        Delete the index for the crawled pages of the root_url.

        :param root_url: the root url to delete
        """
        url = f'{Config.get_base_url()}/docs/delete_crawl'
        req = DeleteCrawlRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            root_url=root_url,
        )
        Config.post(url=url, data=req.model_dump_json())

    def configure_chat(
        self,
        persona: str = None,
        negative_response: str = None,
    ):
        """
        Configures custom chatbot behavior for this collection

        NOTE: New configurations could take up to 2 minutes to take effect.

        :param persona: The chatbot's persona, ie "The chatbot will talk like {persona}". Examples:
            - 'a 1600s pirate'
            - 'a helpful assistant'
        :param negative_response: Chatbot's response when it cannot find the answer,
                                  ie "say {negative_response} if you don't know the answer". Examples:
            - 'i don't know, please reach out to #help for help'
        """
        req = ConfigureChatRequest(
            namespace_name=Config.namespace,
            collection_name=self.name,
            chat_attributes=ChatAttributes(
                persona=persona,
                negative_response=negative_response,
            )
        )

        url = f'{Config.get_base_url()}/docs/configure_chat'
        Config.post(url=url, data=req.model_dump_json())

def describe_response_to_collection(
    collection_name: str,
    resp: DescribeCollectionResponse
) -> Collection:
    description = ""
    if resp.description is not None:
        description = resp.description
    public_read = False
    if resp.public_read is not None:
        public_read = resp.public_read
    return Collection(
        name=collection_name,
        description=description,
        public_read=public_read
    )
