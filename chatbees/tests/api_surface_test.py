import os
import unittest

import requests_mock

import chatbees as ndb
from chatbees.client_models.collection import Collection
from chatbees.server_models.collection_api import (
    ListCollectionsResponse, DescribeCollectionResponse,
)
from chatbees.server_models.doc_api import (
    AskResponse,
    AnswerReference,
    SummaryResponse,
    ListDocsResponse,
)


class APISurfaceTest(unittest.TestCase):
    API_KEY = 'fakeapikey'
    NAMESPACE = 'fakenamespace'
    API_ENDPOINT = 'https://public.us-west-2.aws.chatbees.ai'

    def setUp(self):
        ndb.init(api_key=APISurfaceTest.API_KEY, namespace=APISurfaceTest.NAMESPACE)

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
                '{"namespace_name":"fakenamespace","collection_name":"fakename",'
                '"description":"descr","public_read":false}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/create',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        assert ndb.create_collection(
            Collection(name='fakename', description='descr'))

    @requests_mock.mock()
    def test_create_public_collection(self, mock):
        def match_request_text(request):
            return request.text == (
                '{"namespace_name":"fakenamespace","collection_name":"fakename",'
                '"description":"descr","public_read":true}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/create',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        assert ndb.create_collection(
            Collection(name='fakename', description='descr', public_readable=True))

    @requests_mock.mock()
    def test_list_collections(self, mock):
        resp = ListCollectionsResponse(names=['a', 'b', 'c'])

        def match_request_text(request):
            return request.text == '{"namespace_name":"fakenamespace"}'

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
            return request.text == '{"namespace_name":"fakenamespace","collection_name":"fakename"}'

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/delete',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        ndb.delete_collection('fakename')

    @requests_mock.mock()
    def test_ask(self, mock):
        def match_request_text(request):
            return request.text == (
                '{"namespace_name":"fakenamespace","collection_name":"fakename",'
                '"question":"what is the meaning of life?","top_k":5,'
                '"doc_name":null,"history_messages":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=AskResponse(
                answer='42',
                refs=[AnswerReference(doc_name="doc", page_num=1, sample_text="")]
            ).model_dump_json(),
        )

        answer, _ = ndb.collection('fakename').ask(
            "what is the meaning of life?")
        assert answer == '42'

        def match_request_text2(request):
            return request.text == (
                '{"namespace_name":"fakenamespace","collection_name":"fakename",'
                '"question":"what is the meaning of life?","top_k":2,'
                '"doc_name":null,"history_messages":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text2,
            text=AskResponse(
                answer='42',
                refs=[AnswerReference(doc_name="doc", page_num=1, sample_text="")]
            ).model_dump_json(),
        )

        answer, _ = ndb.collection('fakename').ask(
            "what is the meaning of life?", 2)
        assert answer == '42'

        @requests_mock.mock()
        def test_api_key_required(self, mock):
            # require API key for all APIs
            ndb.init(api_key=None, namespace=APISurfaceTest.NAMESPACE)
            collection = ndb.collection('foo')
            self.assertRaises(ValueError, ndb.list_collections)
            self.assertRaises(ValueError, ndb.delete_collection, 'foo')
            self.assertRaises(ValueError, ndb.create_collection, ndb.collection('foo'))
            fname = f'{os.path.dirname(os.path.abspath(__file__))}/data/text_file.txt'
            self.assertRaises(ValueError, collection.upload_document, fname)

            # The only exception is ask() API for openai-web collection
            def match_request_text(request):
                return request.text == (
                    '{"namespace_name":"fakenamespace","collection_name":"openai-web",'
                    '"question":"what is the meaning of life?","top_k":5,'
                    '"doc_name":null,"history_messages":null}')

            mock.register_uri(
                'POST',
                f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
                additional_matcher=match_request_text,
                text=AskResponse(
                    answer='42',
                    refs=[AnswerReference(doc_name="doc", page_num=1, sample_text="")]
                ).model_dump_json(),
            )

            answer, _ = ndb.collection('openai-web').ask(
                "what is the meaning of life?")
            assert answer == '42'

    @requests_mock.mock()
    def test_describe_collection(self, mock):
        def match_request_text(request):
            return request.text == '{"namespace_name":"fakenamespace","collection_name":"fakename"}'

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/collections/describe',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=DescribeCollectionResponse().model_dump_json(),
        )

        ndb.describe_collection('fakename')

    @requests_mock.mock()
    def test_chat(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"openai-web",'
                                    '"question":"q1","top_k":5,'
                                    '"doc_name":null,'
                                    '"history_messages":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            additional_matcher=match_request_text,
            text=AskResponse(
                answer='a1',
                refs = [AnswerReference(doc_name="doc", page_num=1, sample_text="")]
            ).model_dump_json(),
        )

        chat = ndb.collection('openai-web').chat()
        chat.ask("q1")


        def match_request_text2(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"openai-web",'
                                    '"question":"q2","top_k":3,'
                                    '"doc_name":null,'
                                    '"history_messages":[["q1","a1"]]}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            additional_matcher=match_request_text2,
            text=AskResponse(
                answer='a2',
                refs = [AnswerReference(doc_name="doc", page_num=1, sample_text="")]
            ).model_dump_json(),
        )
        chat.ask("q2", 3)
        assert(chat.history_messages == [('q1', 'a1'), ('q2', 'a2')])

    @requests_mock.mock()
    def test_summary(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"fakename",'
                                    '"doc_name":"path/to/file"}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/summary',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=SummaryResponse(
                summary='test summary',
            ).model_dump_json(),
        )

        assert(ndb.collection('fakename').summarize_document("path/to/file") == "test summary")

    @requests_mock.mock()
    def test_delete_doc(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"fakename",'
                                    '"doc_name":"path/to/file"}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/delete',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        ndb.collection('fakename').delete_document("path/to/file")

    @requests_mock.mock()
    def test_list_documents(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"fakename"}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/list',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=ListDocsResponse(
                doc_names=['doc1', 'doc2'],
            ).model_dump_json(),
        )

        doc_names = ndb.collection('fakename').list_documents()
        assert 2 == len(doc_names)
        assert 'doc1' == doc_names[0]
        assert 'doc2' == doc_names[1]

    @requests_mock.mock()
    def test_configure_chat(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"fakename","chat_attributes":{"persona":"persona",'
                                    '"negative_response":"negative_resp"}}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/configure_chat',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text)

        ndb.collection('fakename').configure_chat('persona', 'negative_resp')
