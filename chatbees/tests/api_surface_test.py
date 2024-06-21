import os
import unittest

import requests_mock

import chatbees as cb
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
from chatbees.server_models.ingestion_api import (
    CreateIngestionResponse,
)
from chatbees.utils.config import Config


class APISurfaceTest(unittest.TestCase):
    API_KEY = 'fakeapikey'
    ACCOUNT_ID = 'fakeaccountid'
    NAMESPACE = 'fakenamespace'
    API_ENDPOINT = None

    def setUp(self):
        cb.init(api_key=APISurfaceTest.API_KEY,
                account_id=APISurfaceTest.ACCOUNT_ID,
                namespace=APISurfaceTest.NAMESPACE)
        APISurfaceTest.API_ENDPOINT = Config.get_base_url()

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

        assert cb.create_collection(
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

        assert cb.create_collection(
            Collection(name='fakename', description='descr', public_read=True))

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
        assert set(cb.list_collections()) == {'a', 'b', 'c'}

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

        cb.delete_collection('fakename')

    @requests_mock.mock()
    def test_ask(self, mock):
        def match_request_text(request):
            return request.text == (
                '{"namespace_name":"fakenamespace","collection_name":"fakename",'
                '"question":"what is the meaning of life?","top_k":5,'
                '"doc_name":null,"history_messages":null,"conversation_id":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=AskResponse(
                answer='42',
                refs=[AnswerReference(doc_name="doc", page_num=1, sample_text="")],
                request_id='id1',
                conversation_id='id1',
            ).model_dump_json(),
        )

        resp = cb.collection('fakename').ask("what is the meaning of life?")
        assert resp.answer == '42'
        assert resp.request_id == 'id1'

        def match_request_text2(request):
            return request.text == (
                '{"namespace_name":"fakenamespace","collection_name":"fakename",'
                '"question":"what is the meaning of life?","top_k":2,'
                '"doc_name":null,"history_messages":null,"conversation_id":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text2,
            text=AskResponse(
                answer='42',
                refs=[AnswerReference(doc_name="doc", page_num=1, sample_text="")],
                request_id='id2',
                conversation_id='id2',
            ).model_dump_json(),
        )

        resp = cb.collection('fakename').ask("what is the meaning of life?", 2)
        assert resp.answer == '42'
        assert resp.request_id == 'id2'

        @requests_mock.mock()
        def test_api_key_required(self, mock):
            # require API key for all APIs
            cb.init(api_key=None, namespace=APISurfaceTest.NAMESPACE)
            collection = cb.collection('foo')
            self.assertRaises(ValueError, cb.list_collections)
            self.assertRaises(ValueError, cb.delete_collection, 'foo')
            self.assertRaises(ValueError, cb.create_collection, cb.collection('foo'))
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
                    refs=[AnswerReference(doc_name="doc", page_num=1, sample_text="")],
                    request_id='id1',
                    conversation_id='id1',
                ).model_dump_json(),
            )

            answer, _ = cb.collection('openai-web').ask(
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

        cb.describe_collection('fakename')

    @requests_mock.mock()
    def test_chat(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"openai-web",'
                                    '"question":"q1","top_k":5,'
                                    '"doc_name":null,'
                                    '"history_messages":null,'
                                    '"conversation_id":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            additional_matcher=match_request_text,
            text=AskResponse(
                answer='a1',
                refs = [AnswerReference(doc_name="doc", page_num=1, sample_text="")],
                request_id='id1',
                conversation_id='id1',
            ).model_dump_json(),
        )

        chat = cb.collection('openai-web').chat()
        resp = chat.ask("q1")
        assert resp.answer == 'a1'
        assert resp.request_id == 'id1'
        assert resp.conversation_id == 'id1'
        assert chat.conversation_id == 'id1'


        def match_request_text2(request):
            return request.text == ('{"namespace_name":"fakenamespace",'
                                    '"collection_name":"openai-web",'
                                    '"question":"q2","top_k":3,'
                                    '"doc_name":null,'
                                    '"history_messages":[["q1","a1"]],'
                                    '"conversation_id":"id1"}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/ask',
            additional_matcher=match_request_text2,
            text=AskResponse(
                answer='a2',
                refs = [AnswerReference(doc_name="doc", page_num=1, sample_text="")],
                request_id='id2',
                conversation_id='id1',
            ).model_dump_json(),
        )
        resp = chat.ask("q2", 3)
        assert(chat.history_messages == [('q1', 'a1'), ('q2', 'a2')])
        assert resp.answer == 'a2'
        assert resp.request_id == 'id2'
        assert resp.conversation_id == 'id1'
        assert chat.conversation_id == 'id1'

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

        assert(cb.collection('fakename').summarize_document("path/to/file") == "test summary")

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

        cb.collection('fakename').delete_document("path/to/file")

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

        doc_names = cb.collection('fakename').list_documents()
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

        cb.collection('fakename').configure_chat('persona', 'negative_resp')

    @requests_mock.mock()
    def test_create_ingestion(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace","collection_name":"fakename","connector_id":"fake_connector_id","type":"CONFLUENCE","spec":{"token":null,"schedule":null,"url":"fakeurl","username":null,"space":"fakespace","cql":null}}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/create_ingestion',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
            text=CreateIngestionResponse(
                ingestion_id='ingestion_id1',
            ).model_dump_json(),
        )

        spec = cb.ConfluenceSpec(url='fakeurl', space='fakespace')
        ingestion_id = cb.collection('fakename').create_ingestion(
            'fake_connector_id', cb.IngestionType.CONFLUENCE, spec)
        assert ingestion_id == 'ingestion_id1'

    @requests_mock.mock()
    def test_update_periodic_ingestion(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace","collection_name":"fakename","type":"CONFLUENCE","spec":{"token":null,"schedule":{"cron_expr":"0 0 * * 0","timezone":"UTC"},"url":"fakeurl","username":null,"space":"fakespace","cql":null}}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/docs/update_periodic_ingestion',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        schedule_spec = cb.ScheduleSpec(cron_expr='0 0 * * 0', timezone='UTC')
        spec = cb.ConfluenceSpec(schedule=schedule_spec,
                                  url='fakeurl',
                                  space='fakespace')
        cb.collection('fakename').update_periodic_ingestion(
            cb.IngestionType.CONFLUENCE, spec)

    @requests_mock.mock()
    def test_create_or_update_feedback(self, mock):
        def match_request_text(request):
            return request.text == ('{"namespace_name":"fakenamespace","collection_name":"fakename","request_id":"id","thumb_down":true,"text_feedback":"text feedback","unregistered_user":null}')

        mock.register_uri(
            'POST',
            f'{APISurfaceTest.API_ENDPOINT}/feedback/create_or_update',
            request_headers={'api-key': 'fakeapikey'},
            additional_matcher=match_request_text,
        )

        cb.collection('fakename').create_or_update_feedback(
            'id', True, 'text feedback')
