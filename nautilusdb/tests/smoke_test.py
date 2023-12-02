import io
import os
import unittest
import uuid

import nautilusdb as ndb
from nautilusdb import ColumnType


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
        col = (
            ndb.CollectionBuilder.question_answer(unique_col).build())
        return ndb.create_collection(col)

    def test_vector_apis(self):
        owner = self.apikey1
        ndb.init(owner)
        unique_col = 'cl-' + uuid.uuid4().hex
        col = (ndb.CollectionBuilder()
               .set_name(unique_col)
               .set_dimension(2)
               .add_metadata_column('int_col', ColumnType.Int)
               .add_metadata_column('str_col', ColumnType.String)
               .build())
        ndb.create_collection(col)

        try:
            col.upsert_vector([
                ndb.Vector(vid="abc123", embedding=[1.1, 2.2],
                           metadata={'int_col': 1, 'str_col': 'abc123'})])
            col.upsert_vector([
                ndb.Vector(vid="abc", embedding=[1.1, 2.2],
                           metadata={'int_col': 2, 'str_col': 'abc'})])
            col.upsert_vector(
                [
                    ndb.Vector(vid="123", embedding=[1.1, 2.2]),
                    ndb.Vector(vid="124", embedding=[1.1, 2.2]),
                    ndb.Vector(vid="125", embedding=[1.1, 2.2]),
                ])

            # Upsert is idempotent
            col.upsert_vector(
                [
                    ndb.Vector(vid="123", embedding=[1.1, 2.2]),
                    ndb.Vector(vid="124", embedding=[1.1, 2.2]),
                    ndb.Vector(vid="125", embedding=[1.1, 2.2]),
                ])

            # Delete vectors
            col.delete_vectors(vector_ids=['123', '124'])
            col.delete_vectors(metadata_filter="int_col is null")
            col.delete_vectors(metadata_filter="int_col >= 2")
            col.delete_vectors(delete_all=True)
        finally:
            ndb.delete_collection(col.name)

    def test_search_metadata_filter(self):
        owner = self.apikey1
        ndb.init(owner)
        unique_col = 'cl-' + uuid.uuid4().hex

        # Create a collection with a few different metadata columns
        col = (ndb.CollectionBuilder()
               .set_name(unique_col)
               .set_dimension(2)
               .add_metadata_column('int_column', ndb.ColumnType.Int)
               .add_metadata_column('float_column', ndb.ColumnType.Float)
               .add_metadata_column('double_column', ndb.ColumnType.Double)
               .add_metadata_column('string_column', ndb.ColumnType.String)
               .add_metadata_column('bytes_column', ndb.ColumnType.Bytes)
               .add_metadata_column('boolean_column', ndb.ColumnType.Boolean)
               .build())
        ndb.create_collection(col)

        try:
            # Vector 1-3 are at (1, 1) - (3, 3) with all metadata columns populated
            # Vector 10-30 are at (10, 10) - (30, 30) with some metadata columns populated
            # Vector 100-300 are at (100, 100) - (300, 300) with no metadata columns populated
            col.upsert_vector(
                [
                    ndb.Vector(
                        vid="1",
                        embedding=[1.0, 1.0],
                        metadata={
                            'int_column': 1,
                            'float_column': 1.0,
                            'double_column': 1.0,
                            'string_column': "vector at 1.0, 1.0",
                            'boolean_column': True,
                        }),
                    ndb.Vector(
                        vid="2",
                        embedding=[2.0, 2.0],
                        metadata={
                            'int_column': 2,
                            'float_column': 2.0,
                            'double_column': 2.0,
                            'string_column': "vector at 2.0, 2.0",
                            'boolean_column': True,
                        }),
                    ndb.Vector(
                        vid="3",
                        embedding=[3.0, 3.0],
                        metadata={
                            'int_column': 3,
                            'float_column': 3.0,
                            'double_column': 3.0,
                            'string_column': "vector at 3.0, 3.0",
                            'boolean_column': True,
                        }),
                    ndb.Vector(
                        vid="10",
                        embedding=[10.0, 10.0],
                        metadata={'int_column': 10, 'float_column': 10.0, 'double_column': 10.0}),
                    ndb.Vector(
                        vid="20",
                        embedding=[20.0, 20.0],
                        metadata={'int_column': 20, 'float_column': 20.0, 'double_column': 20.0}),
                    ndb.Vector(
                        vid="30",
                        embedding=[30.0, 30.0],
                        metadata={'int_column': 30, 'float_column': 30.0, 'double_column': 30.0}),
                    ndb.Vector(vid="100", embedding=[100.0, 100.0]),
                    ndb.Vector(vid="200", embedding=[200.0, 200.0]),
                    ndb.Vector(vid="300", embedding=[300.0, 300.0]),
                ])

            # all search queries are constructed with a vector at [0.1, 0.1]. The closest vectors
            # are 1, 2, 3, 10, 20, 30, 100, 200, 300 in that order

            filter_and_expectations = {
                # Test No filter
                None: {'1', '2', '3'},

                # Test simple filter
                "int_column != 1": {'2', '3', '10'},
                "int_column = 10": {'10'},

                # Test AND
                "int_column > 1 and float_column <= 3.1": {'2', '3'},

                # Test OR
                "int_column = 1 or int_column = 2 or int_column = 3": {'1', '2', '3'},

                # Test NOT
                "int_column != 1 and not int_column = 2": {'3', '10', '20'},

                # Test is/is not null
                "int_column is null": {'100', '200', '300'},
                "int_column is not null and float_column > 3.1": {'10', '20', '30'},

                # Test arithmetics
                "int_column + 1 = 2": {'1'},
                "int_column % 2 = 0": {'2', '10', '20'},

                # Test parenthesis
                "(int_column < 100 and int_column > 10) or int_column < 2": {'1', '20', '30'},

                # Test other columns
                "string_column = 'vector at 3.0, 3.0' or boolean_column = false": {'3'},
                "boolean_column = true": {'1', '2', '3'},
            }

            # Search requests
            requests = [ndb.SearchRequest(embedding=[0.1, 0.1], metadata_filter=ftr) for ftr
                        in filter_and_expectations.keys()]
            results = col.search(requests)
            actual_ids = [{vector.vid for vector in result.vectors} for result in results]
            assert len(actual_ids) == len(requests)

            for i in range(len(actual_ids)):
                ftr = requests[i].metadata_filter
                expectation = filter_and_expectations[ftr]
                assert actual_ids[i] == expectation, (f"Expected {expectation}, got "
                                                      f"{actual_ids[i]} for filter {ftr}")
            # Query requests
            requests = [ndb.QueryRequest(metadata_filter=ftr) for ftr
                        in filter_and_expectations.keys() if ftr is not None]
            results = col.query(requests)
            actual_ids = [{vector.vid for vector in result.vectors} for result in results]
            assert len(actual_ids) == len(requests)

            for i in range(len(actual_ids)):
                ftr = requests[i].metadata_filter
                expectation = filter_and_expectations[ftr]
                assert actual_ids[i] == expectation, (f"Expected {expectation}, got "
                                                      f"{actual_ids[i]} for filter {ftr}")

        finally:
            # Delete is idempotent
            ndb.delete_collection(col.name)

    def test_file_upload_and_ask(self):
        owner = self.apikey1
        ndb.init(owner)
        unique_col = 'cl-' + uuid.uuid4().hex

        # Create a collection with a few different metadata columns
        col = ndb.CollectionBuilder.question_answer(unique_col).build()
        ndb.create_collection(col)

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
            chat2 = col.chat()

            chat1.ask("q1")
            chat1.ask("q2")
            chat1.ask("q3")
            chat2.ask("q1")
            chat2.ask("q2")
            chat2.ask("q3")
        finally:
            ndb.delete_collection(col.name)
