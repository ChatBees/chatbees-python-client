import hashlib
import logging
import os
import unittest
from typing import List

import chatbees as cb
from chatbees import Chat
from chatbees.server_models.application import ApplicationType
from chatbees.server_models.collection_api import ChatAttributes
from chatbees.server_models.doc_api import AnswerReference, ExtractType, ExtractedTable
from chatbees.utils.ask import ask_application

TEST_AID = os.environ.get('ENV_TEST_AID')
TEST_APIKEY = os.environ.get('ENV_TEST_APIKEY')

class LocalfsImplTest(unittest.TestCase):
    aid: str
    apikey: str

    def setUp(self):
        self.aid = TEST_AID
        self.apikey = TEST_APIKEY
        cb.init(api_key=self.apikey, account_id=self.aid)

    def ask(self, clname: str, q: str, top_k: int = 5):
        col = cb.Collection(name=clname)
        resp = col.ask(q, top_k)
        logging.info(f"{clname} q={q} a={resp.answer}")
        doc_names = [ref.doc_name for ref in resp.refs]
        logging.info(f"refs={doc_names}")

    def ask_app(self, app_name: str, q: str, top_k: int = 5):
        resp = ask_application(application_name=app_name, question=q, top_k=top_k)
        logging.info(f"{app_name} q={q} a={resp.answer}")
        doc_names = [ref.doc_name for ref in resp.refs]
        logging.info(f"refs={doc_names}")

    def test_applications(self):
        clname = 'test_applications'
        try:
            col = cb.Collection(name=clname)
            cb.create_collection(col)
            cb.create_collection_application(
                application_name='test',
                description='testdesc',
                collection_name=clname,
                chat_attrs=ChatAttributes(welcome_msg='TEST welcome!',
                                          negative_response='TEST negative'))
            cb.create_gpt_application(application_name='test2', provider='openai', model='4o')
            applications = cb.list_applications()
            assert set([app.application_name for app in applications]) == {'test', 'test2'}

            app = applications[0] if applications[0].application_name == 'test' else applications[1]

            # Application info is persisted
            assert app.application_desc == 'testdesc'
            assert app.chat_attrs.welcome_msg == 'TEST welcome!'
            assert app.chat_attrs.negative_response == 'TEST negative'

            # Upload a test file, then ask an unrelated question. should get configured negative
            # response back
            test_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/text_file.txt'
            col.upload_document(test_file)

            # Asking through APP should respect negative_response.
            # It is not configured through cl
            app_answer = Chat(application_name=app.application_name).ask('what is openai?').answer
            cl_answer = col.chat().ask('what is openai?').answer
            assert app_answer == 'TEST negative', f'App answer {app_answer}'
            assert cl_answer != 'TEST negative', f"Cl answer {cl_answer}"

            cb.delete_application('test')
            cb.delete_application('test2')
        except Exception:
            cb.delete_collection(clname)

    def test_doc_apis(self):
        clname = 'test_doc_apis'

        # Create a collection and an application
        col = cb.Collection(name=clname)
        cb.create_collection(col)

        app = cb.create_collection_application('testapp', collection_name=clname)

        files = [
            f'{os.path.dirname(os.path.abspath(__file__))}/data/text_file.txt',
            f'{os.path.dirname(os.path.abspath(__file__))}/data/española.txt',
            f'{os.path.dirname(os.path.abspath(__file__))}/data/française.txt',
            f'{os.path.dirname(os.path.abspath(__file__))}/data/中文.txt',
        ]
        doc_names = {'text_file.txt', 'española.txt', 'française.txt', '中文.txt'}

        try:
            # add and summarize
            for file in files:
                col.upload_document(file)
                fname = os.path.basename(file)
                col.summarize_document(fname)

            # list
            print("list_documents")
            list_doc_names = col.list_documents()
            assert doc_names == set(list_doc_names)

            # ask
            print("ask")
            resp = col.ask('question?')
            assert len(resp.refs) > 0

            # delete, then list and ask again
            col.delete_document('española.txt')
            doc_names = {'text_file.txt', 'française.txt', '中文.txt'}

            list_doc_names = col.list_documents()
            assert doc_names == set(list_doc_names)

            resp = col.ask('question?')
            assert len(resp.refs) > 0

            # chat
            chat1 = col.chat()
            app_chat1 = Chat(application_name=app.application_name)
            chat2 = col.chat(doc_name="text_file.txt")
            app_chat2 = Chat(application_name=app.application_name, doc_name='text_file.txt')

            chat1.ask("q1")
            chat1.ask("q2")
            app_chat1.ask("q1")
            app_chat1.ask("q2")

            resp = chat2.ask("q1")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")
            resp = chat2.ask("q2")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")

            resp = app_chat2.ask("q1")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")
            resp = app_chat2.ask("q2")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")

            print(f"Convo {resp.conversation_id}")

            # ensure we can configure chat attrs
            col.configure_chat('a pirate from 1600s', 'the word snowday and nothing else')
            resp = col.ask('what is the color of my hair?')
            print("persona answer", resp.answer)

            resp = app_chat1.ask('what is the color of my hair?')
            print("[app] persona answer", resp.answer)

        finally:
            cb.delete_application(app.application_name)
            cb.delete_collection(col.name)

    def assertRefsAreFromDoc(self, refs: List[AnswerReference], doc: str):
        assert len(refs) > 0
        for ref in refs:
            assert ref.doc_name == doc

    def get_file_md5(self, path):
        with open(path, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            return hashlib.md5(data).hexdigest()
    def test_fs(self):
        try:
            cols = cb.list_collections()
            assert 'another_collection' not in cols

            # Create another collection
            col = cb.Collection(name='another_collection')
            cb.create_collection(col)

            cols = cb.list_collections()
            assert 'another_collection' in cols

            # List docs, should be empty
            docs = col.list_documents()
            assert docs == []

            # Upload transformer pdf and ask question
            doc_name = 'transformer.pdf'

            file_md5 = self.get_file_md5(doc_name)

            col.upload_document(doc_name)
            downloaded = col.download_document(doc_name, './downloads')
            assert file_md5 == self.get_file_md5(downloaded), f'MD5 mismatch. original={doc_name}, downloaded={downloaded}'

            q = 'what is a transformer?'
            print(f"[global] q: {q}, a={col.ask('what is a transformer')}")
            print(f"[doc] q: {q}, a={col.ask('what is a transformer', doc_name=doc_name)}")

            # List docs, should see doc_name
            docs = col.list_documents()
            assert doc_name in docs, f'Documents are {docs}'

            col.delete_document(doc_name)

            # Describe, delete Delete
            desc = cb.describe_collection('another_collection')
            print(desc)
        finally:
            cb.delete_collection('another_collection')

    def _test_doc(self, clname1: str, clname2: str, write: bool = True):
        cols = cb.list_collections()
        logging.info(f"cols={cols}")

        # upload_document
        col = cb.Collection(name=clname1)
        doc_name = 'transformer-paper.pdf'
        if write:
            col.upload_document(doc_name)
        self.ask(clname1, 'what is transformer?')

        summary = col.summarize_document(doc_name)
        logging.info(f"doc={doc_name} summary={summary}")

        # test outline_faqs
        outline_faqs = col.get_document_outline_faq(doc_name)
        logging.info(f"doc={doc_name} outlines={len(outline_faqs.outlines)} "
                     f"{outline_faqs.outlines}, faqs={len(outline_faqs.faqs)} "
                     f"{outline_faqs.faqs}")

        # docs.piratenation.game has 49 pages
        col = cb.collection(clname2)

        docs = col.list_documents()
        docs.sort()
        logging.info(f"docs={len(docs)} {docs}")

        q = 'what is pirate nation?'
        self.ask(clname2, q)
