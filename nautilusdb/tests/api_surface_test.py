import unittest
import requests_mock

import nautilusdb as ndb
from nautilusdb import CollectionBuilder, Vector
from nautilusdb.server_models.api import (
    ListCollectionsResponse,
    UpsertResponse,
)
from nautilusdb.server_models.app_api import AskResponse, AnswerReference


class APISurfaceTest(unittest.TestCase):
    API_KEY = 'fakeapikey'
    API_ENDPOINT = 'https://public.us-west-2.aws.nautilusdb.com'

    def setUp(self):
        ndb.init(api_key=APISurfaceTest.API_KEY)

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
                '{"name":"fakename","dimension":10,'
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
                '{"name":"fakename","dimension":1536,'
                '"description":"This is a demo collection. '
                'Embeddings are generated using OpenAI ada_002 server_models",'
                '"metas":{"text":"string","tokens":"int","filename":"string"}}')

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
        mock.register_uri(
            'GET',
            f'{APISurfaceTest.API_ENDPOINT}/collections/list',
            request_headers={'api-key': 'fakeapikey'},
            text=resp.model_dump_json(),
        )

        collections = ndb.list_collections()
        assert {col.name for col in collections} == {'a', 'b', 'c'}

    @requests_mock.mock()
    def test_delete_collection(self, mock):
        def match_request_text(request):
            return request.text == '{"name":"fakename"}'

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
                '{"collection_name":"fakename",'
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
                '{"collection_name":"fakename",'
                '"question":"what is the meaning of life?"}')

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
