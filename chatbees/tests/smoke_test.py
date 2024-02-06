import io
import os
import time
import unittest
import uuid
from typing import List

import chatbees as ndb
from chatbees.server_models.doc_api import CrawlStatus
from chatbees.client_models.doc import AnswerReference


class SmokeTest(unittest.TestCase):
    """
    Verifies basic functionality of client. Not a hermetic test, it invokes real
    chatbees APIs
    """
    apikey1: str
    apikey2: str

    def setUp(self):
        # TODO: Replace hard-coded API key with dynamically created keys when
        # TODO: we have the ability to delete API keys
        #self.apikey1 = 'MS1hOTJmZDE1Ni1lNTg1LTcyM2ItMzZiNy0yYjEyYzdjZDQ3ZWE='
        #self.apikey2 = 'MS1iMjA0ZDc1Yi03MTc5LTZlMTgtMjBmMC02OWQzODZiOTExZDM='
        self.apikey1 = ndb.create_api_key()
        self.apikey2 = ndb.create_api_key()

    def test_invalid_api_key(self):
        ndb.init(api_key='invalid')

        # Invalid api_key triggers exception
        self.assertRaises(ndb.UnAuthorized, ndb.list_collections)

    def test_collection_apis(self):
        # Clear API key from config
        apikey1 = self.apikey1
        apikey2 = self.apikey2

        # Create private collections, one for each created key
        ndb.init(api_key=apikey1)
        private_col_key1 = self.create_collection()

        ndb.init(api_key=apikey2)
        private_col_key2 = self.create_collection()

        try:
            # List collections using API key1
            ndb.init(api_key=apikey1)
            collections_visible_to_key1 = set(ndb.list_collections())
            assert private_col_key2.name not in collections_visible_to_key1
            assert private_col_key1.name in collections_visible_to_key1
            # Key1 is not authorized to delete a collection created by key2
            self.assertRaises(ndb.UnAuthorized, ndb.delete_collection, private_col_key2.name)

            # List collections using API key2
            ndb.init(api_key=apikey2)
            collections_visible_to_key2 = set(ndb.list_collections())
            assert private_col_key1.name not in collections_visible_to_key2
            assert private_col_key2.name in collections_visible_to_key2
            # Key2 is not authorized to delete a collection created by key1
            self.assertRaises(ndb.UnAuthorized, ndb.delete_collection, private_col_key1.name)

        finally:
            # key1 is authorized to delete its own collections as well as public
            # collections
            ndb.init(api_key=apikey1)
            ndb.delete_collection(private_col_key1.name)

            ndb.init(api_key=apikey2)
            ndb.delete_collection(private_col_key2.name)

    def create_collection(self, public_readable: bool=False) -> ndb.Collection:
        unique_col = 'cl_' + uuid.uuid4().hex
        col = ndb.Collection(name=unique_col, public_readable=public_readable)
        return ndb.create_collection(col)

    def test_public_collection(self):
        owner = self.apikey1
        ndb.init(owner)
        col = self.create_collection(public_readable=True)
        col.upload_document(f'{os.path.dirname(os.path.abspath(__file__))}/data/text_file.txt')

        # Clear API key and ask questions again
        ndb.init(api_key=None)
        col.ask('should not fail')

    def test_doc_apis(self):
        owner = self.apikey1
        ndb.init(owner)
        col = self.create_collection()

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

            # ask with top_k
            print("ask")
            a, refs = col.ask('question?', 4)
            assert 4 == len(refs)

            # delete, then list and ask again
            col.delete_document('española.txt')
            doc_names = {'text_file.txt', 'française.txt', '中文.txt'}

            list_doc_names = col.list_documents()
            assert doc_names == set(list_doc_names)

            a, refs = col.ask('question?', 4)
            assert 4 == len(refs)

            # chat
            chat1 = col.chat()
            chat2 = col.chat(doc_name="text_file.txt")

            chat1.ask("q1")
            chat1.ask("q2")
            chat1.ask("q3")

            a, refs = chat2.ask("q1")
            self.assertRefsAreFromDoc(refs, "text_file.txt")
            a, refs = chat2.ask("q2")
            self.assertRefsAreFromDoc(refs, "text_file.txt")
            a, refs = chat2.ask("q3")
            self.assertRefsAreFromDoc(refs, "text_file.txt")

            # ensure we can configure chat attrs
            col.configure_chat('a pirate from 1600s', 'the word snowday and nothing else')
            ans, ref = col.ask('what is the color of my hair?')
        finally:
            ndb.delete_collection(col.name)

    def assertRefsAreFromDoc(self, refs: List[AnswerReference], doc: str):
        assert len(refs) > 0
        for ref in refs:
            assert ref.doc_name == doc

    def test_crawl_apis(self):
        owner = self.apikey1
        ndb.init(owner)
        col = self.create_collection()

        try:
            crawl_id = col.create_crawl('https://www.openai.com', 10)

            max_waits = 100
            waits = 0
            while waits < max_waits:
                status, pages = col.get_crawl(crawl_id)
                if status != CrawlStatus.RUNNING:
                    break
                time.sleep(1)

            assert status == CrawlStatus.SUCCEEDED
            assert 10 == len(pages)

            col.index_crawl(crawl_id)
        finally:
            ndb.delete_collection(col.name)
