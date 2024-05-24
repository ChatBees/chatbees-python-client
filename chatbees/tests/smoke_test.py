import os
import time
import unittest
import uuid
from typing import List


# Only import from chatbees module to make sure classes are exported correctly
import chatbees as cb
from chatbees import (
    Collection,
    IngestionType,
    IngestionStatus,
    NotionSpec,
    ConfluenceSpec,
    AnswerReference,
)


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
        self.apikey1 = cb.create_api_key()
        self.apikey2 = cb.create_api_key()
        print(self.apikey1)
        print(self.apikey2)

    def test_invalid_api_key(self):
        cb.init(api_key='invalid')

        # Invalid api_key triggers exception
        self.assertRaises(cb.UnAuthorized, cb.list_collections)

    def test_collection_apis(self):
        # Clear API key from config
        apikey1 = self.apikey1
        apikey2 = self.apikey2

        # Create private collections, one for each created key
        cb.init(api_key=apikey1)
        private_col_key1 = self.create_collection()

        cb.init(api_key=apikey2)
        private_col_key2 = self.create_collection()

        try:
            # List collections using API key1
            cb.init(api_key=apikey1)
            collections_visible_to_key1 = set(cb.list_collections())
            assert private_col_key2.name not in collections_visible_to_key1
            assert private_col_key1.name in collections_visible_to_key1
            # Key1 is not authorized to delete a collection created by key2
            self.assertRaises(cb.UnAuthorized, cb.delete_collection, private_col_key2.name)

            # List collections using API key2
            cb.init(api_key=apikey2)
            collections_visible_to_key2 = set(cb.list_collections())
            assert private_col_key1.name not in collections_visible_to_key2
            assert private_col_key2.name in collections_visible_to_key2
            # Key2 is not authorized to delete a collection created by key1
            self.assertRaises(cb.UnAuthorized, cb.delete_collection, private_col_key1.name)

        finally:
            # key1 is authorized to delete its own collections as well as public
            # collections
            cb.init(api_key=apikey1)
            cb.delete_collection(private_col_key1.name)

            cb.init(api_key=apikey2)
            cb.delete_collection(private_col_key2.name)

    def create_collection(self, public_read: bool=False) -> cb.Collection:
        unique_col = 'cl_' + uuid.uuid4().hex
        col = cb.Collection(name=unique_col, public_read=public_read)
        return cb.create_collection(col)

    def test_public_collection(self):
        owner = self.apikey1
        cb.init(owner)
        col = self.create_collection(public_read=True)
        col.upload_document(f'{os.path.dirname(os.path.abspath(__file__))}/data/text_file.txt')

        # Clear API key and ask questions again
        cb.init(api_key=None)
        col.ask('should not fail')

        cb.init(owner)
        cb.configure_collection(collection_name=col.name, public_read=False)
        cb.init(api_key=None)
        self.assertRaises(cb.UnAuthorized, col.ask, 'should fail')

        cb.init(owner)
        cb.configure_collection(collection_name=col.name, public_read=True)
        cb.init(api_key=None)
        col.ask('should not fail')

    def test_doc_apis(self):
        owner = self.apikey1
        cb.init(owner)
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
            chat2 = col.chat(doc_name="text_file.txt")

            chat1.ask("q1")
            chat1.ask("q2")
            chat1.ask("q3")

            resp = chat2.ask("q1")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")
            resp = chat2.ask("q2")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")
            resp = chat2.ask("q3")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")

            # ensure we can configure chat attrs
            col.configure_chat('a pirate from 1600s', 'the word snowday and nothing else')
            resp = col.ask('what is the color of my hair?')
            print("persona answer", resp.answer)
        finally:
            cb.delete_collection(col.name)

    def assertRefsAreFromDoc(self, refs: List[AnswerReference], doc: str):
        assert len(refs) > 0
        for ref in refs:
            assert ref.doc_name == doc

    def test_crawl_apis(self):
        owner = self.apikey1
        cb.init(owner)
        col = self.create_collection()

        try:
            root_url = 'https://www.openai.com'
            crawl_id = col.create_crawl(root_url, 3)

            max_waits = 100
            waits = 0
            while waits < max_waits:
                status, pages = col.get_crawl(crawl_id)
                if status != IngestionStatus.RUNNING:
                    break
                time.sleep(2)

            assert status == IngestionStatus.SUCCEEDED
            assert 3 == len(pages)

            col.index_crawl(crawl_id)
            list_doc_names = col.list_documents()
            assert 3 == len(list_doc_names)

            col.delete_crawl(root_url)
            list_doc_names = col.list_documents()
            assert 0 == len(list_doc_names)
        finally:
            cb.delete_collection(col.name)
