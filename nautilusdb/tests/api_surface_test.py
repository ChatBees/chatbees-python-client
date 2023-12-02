import math
import os
import unittest
from typing import List

import requests_mock

import nautilusdb as ndb
from nautilusdb import CollectionBuilder, Vector
from nautilusdb.client_models.search import SearchRequest
from nautilusdb.client_models.query import VectorResponse
from nautilusdb.server_models.collection_api import (
    ListCollectionsResponse, DescribeCollectionResponse,
)
from nautilusdb.server_models.vector_api import (
    UpsertResponse,
    VectorWithScore as ServerVectorWithScore,
)
from nautilusdb.server_models.app_api import AskResponse, AnswerReference, SummaryResponse
from nautilusdb.server_models.search_api import (
    SearchRequest as ServerQueryRequest,
    SearchResponse as ServerQueryResponse,
    VectorResult as ServerQueryResult,
)


class APISurfaceTest(unittest.TestCase):
    API_KEY = 'fakeapikey'
    PROJECT = 'fakeproject'
    API_ENDPOINT = 'https://public.us-west-2.aws.nautilusdb.com'

    def setUp(self):
        ndb.init(api_key=APISurfaceTest.API_KEY, project=APISurfaceTest.PROJECT)

    @requests_mock.mock()
    def test_create_api_key(self, mock):
        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/apikey/create',
            text='{"api_key": "anotherfakeapikey"}',
        )

        assert ndb.create_api_key() == 'anotherfakeapikey'

    @requests_mock.mock()
    def test_create_collection(self, mock):
        def match_request_text(request):
            return request.text == (
                '{"project_name":"fakeproject","collection_name":"fakename","dimension":10,'
                '"description":"descr",' '"metas":{}}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/create',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        assert ndb.create_collection(
            CollectionBuilder()
            .set_name('fakename')
            .set_dimension(10)
            .set_description('descr').build())

    @requests_mock.mock()
    def test_create_qa_collection(self, mock):
        def match_request_text(request):
            return request.text == (
                '{"project_name":"fakeproject","collection_name":"fakename","dimension":1536,'
                '"description":"This is a demo collection. '
                'Embeddings are generated using OpenAI ada_002 server_models",'
                '"metas":{"TEXT":"string","TOKENS":"int","PAGE":"int","FILENAME":"string"}}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/create',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        assert ndb.create_collection(CollectionBuilder.question_answer("fakename").build())

    @requests_mock.mock()
    def test_list_collections(self, mock):
        resp = ListCollectionsResponse(names=['a', 'b', 'c'])

        def match_request_text(request):
            return request.text == '{"project_name":"fakeproject"}'

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/list',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=resp.model_dump_json(),
        )
        assert set(ndb.list_collections()) == {'a', 'b', 'c'}

    @requests_mock.mock()
    def test_delete_collection(self, mock):
        def match_request_text(request):
            return request.text == '{"project_name":"fakeproject","collection_name":"fakename"}'

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/delete',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        ndb.delete_collection('fakename')

    @requests_mock.mock()
    def test_upsert_vector(self, mock):
        def match_request_text(request):
            return request.text == (
                '{"project_name":"fakeproject","collection_name":"fakename",'
                '"vectors":[{"id":"foo","embedding":[1.1,2.2],"metas":null}]}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/vectors/upsert',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=UpsertResponse(upsert_count=1).model_dump_json(),
        )

        assert ndb.collection('fakename').upsert_vector(
            [Vector(vid='foo', embedding=[1.1, 2.2])]) == 1

    @requests_mock.mock()
    def test_ask(self, mock):
        def match_request_text(request):
            return request.text == (
                '{"project_name":"fakeproject","collection_name":"fakename",'
                '"question":"what is the meaning of life?","top_k":5,'
                '"doc_name":null,"history_messages":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/qadocs/ask',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=AskResponse(
                answer='42',
                refs=[AnswerReference(doc_name="doc")]
            ).model_dump_json(),
        )

        answer, _ = ndb.collection('fakename').ask(
            "what is the meaning of life?")
        assert answer == '42'

    @requests_mock.mock()
    def test_search(self, mock):
        def match_request_text(request):
            req = ServerQueryRequest.model_validate_json(request.text)
            return (req.project_name == 'fakeproject'
                    and req.collection_name == 'fakename'
                    and len(req.queries) == 1
                    and req.queries[0].where == 'where clause')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/vectors/search',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=ServerQueryResponse(
                results=[
                    ServerQueryResult(
                        vectors=[
                            ServerVectorWithScore(score=1.0, id='vec')
                        ]
                    )
                ]
            ).model_dump_json(),
        )

        result: List[VectorResponse] = ndb.collection('fakename').search(
            [SearchRequest(embedding=[1.1, 2.2], metadata_filter='where clause')])
        assert len(result) == 1
        assert len(result[0].vectors) == 1
        assert math.isclose(result[0].vectors[0].score, 1.0)
        assert result[0].vectors[0].vid == 'vec'

    @requests_mock.mock()
    def test_api_key_required(self, mock):
        # require API key for all APIs
        ndb.init(api_key=None, project=APISurfaceTest.PROJECT)
        collection = ndb.collection('foo')
        self.assertRaises(ValueError, ndb.list_collections)
        self.assertRaises(ValueError, ndb.delete_collection, 'foo')
        self.assertRaises(ValueError, ndb.create_collection, ndb.collection('foo'))
        self.assertRaises(ValueError, collection.upsert_vector, [])
        self.assertRaises(ValueError, collection.ask, "question")
        fname = f'{os.path.dirname(os.path.abspath(__file__))}/data/text_file.txt'
        self.assertRaises(ValueError, collection.upload_document, fname)

        # The only exception is ask() API for openai-web collection
        def match_request_text(request):
            return request.text == (
                '{"project_name":"fakeproject","collection_name":"openai-web",'
                '"question":"what is the meaning of life?","top_k":5,'
                '"doc_name":null,"history_messages":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/qadocs/ask',
            additional_matcher=match_request_text,
            text=AskResponse(
                answer='42',
                refs=[AnswerReference(doc_name="doc")]
            ).model_dump_json(),
        )

        answer, _ = ndb.collection('openai-web').ask(
            "what is the meaning of life?")
        assert answer == '42'

    @requests_mock.mock()
    def test_describe_collection(self, mock):
        def match_request_text(request):
            return request.text == '{"project_name":"fakeproject","collection_name":"fakename"}'

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/describe',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=DescribeCollectionResponse(
                collection_name='test',
                dimension=2,
                vector_count=1,
            ).model_dump_json(),
        )

        ndb.describe_collection('fakename')

    @requests_mock.mock()
    def test_delete_vectors(self, mock):
        def match_request_text(request):
            return request.text == ('{"project_name":"fakeproject","collection_name":"fakename",'
                                    '"vector_ids":null,"delete_all":false,'
                                    '"where":"a = 1"}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/vectors/delete',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        ndb.collection('fakename').delete_vectors(metadata_filter='a = 1')

    @requests_mock.mock()
    def test_chat(self, mock):
        def match_request_text(request):
            return request.text == ('{"project_name":"fakeproject",'
                                    '"collection_name":"openai-web",'
                                    '"question":"q1","top_k":5,'
                                    '"doc_name":null,'
                                    '"history_messages":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/qadocs/ask',
            additional_matcher=match_request_text,
            text=AskResponse(
                answer='a1',
                refs=[AnswerReference(doc_name="doc")]
            ).model_dump_json(),
        )

        chat = ndb.collection('openai-web').chat()
        chat.ask("q1")


        def match_request_text2(request):
            return request.text == ('{"project_name":"fakeproject",'
                                    '"collection_name":"openai-web",'
                                    '"question":"q2","top_k":5,'
                                    '"doc_name":null,'
                                    '"history_messages":[["q1","a1"]]}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/qadocs/ask',
            additional_matcher=match_request_text2,
            text=AskResponse(
                answer='a2',
                refs=[AnswerReference(doc_name="doc")]
            ).model_dump_json(),
        )
        chat.ask("q2")
        assert(chat.history_messages == [('q1', 'a1'), ('q2', 'a2')])

    @requests_mock.mock()
    def test_summary(self, mock):
        def match_request_text(request):
            return request.text == ('{"project_name":"fakeproject",'
                                    '"collection_name":"fakename",'
                                    '"doc_name":"path/to/file"}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/qadocs/summary',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=SummaryResponse(
                summary='test summary',
            ).model_dump_json(),
        )

        assert(ndb.collection('fakename').summarize_document("path/to/file") == "test summary")
