import io
import os
import unittest
import uuid
from typing import List

import nautilusdb as ndb
from nautilusdb import ColumnType
from nautilusdb.client_models.doc import AnswerReference


class SmokeTest(unittest.TestCase):
    """
    Verifies basic functionality of client. Not a hermetic test, it invokes real
    nautilusdb APIs
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

    def create_collection(self) -> ndb.Collection:
        unique_col = 'cl-' + uuid.uuid4().hex
        col = ndb.Collection(name=unique_col)
        return ndb.create_collection(col)

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

        try:
            for file in files:
                col.upload_document(file)
                fname = os.path.basename(file)
                col.summarize_document(fname)
            col.ask('question?')

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
        finally:
            ndb.delete_collection(col.name)

    def assertRefsAreFromDoc(self, refs: List[AnswerReference], doc: str):
        assert len(refs) > 0
        for ref in refs:
            assert ref.doc_name == doc
