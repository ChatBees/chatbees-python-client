import logging
import os
import time
import unittest
import uuid
from typing import List, Any

import chatbees as cb
from chatbees.server_models.doc_api import AnswerReference

TEST_AID = os.environ.get('ENV_TEST_AID')
TEST_APIKEY = os.environ.get('ENV_TEST_APIKEY')

TEST_CONFLUENCE_USER = os.environ.get('TEST_CONFLUENCE_USER')
TEST_CONFLUENCE_TOKEN = os.environ.get('TEST_CONFLUENCE_TOKEN')
TEST_CONFLUENCE_URL = os.environ.get('TEST_CONFLUENCE_URL')
TEST_CONFLUENCE_SPACE = os.environ.get('TEST_CONFLUENCE_SPACE')

class RegressionTest(unittest.TestCase):
    aid: str
    apikey: str

    def setUp(self):
        self.aid = TEST_AID
        self.apikey = TEST_APIKEY

    def crawl_web(self, clname: str, root_url: str, max_urls_to_crawl: int = 200):
        col = cb.Collection(name=clname)

        crawl_id = col.create_crawl(root_url, max_urls_to_crawl)

        max_waits = 100
        waits = 0
        while waits < max_waits:
            status, pages = col.get_crawl(crawl_id)
            if status != cb.CrawlStatus.RUNNING:
                logging.info(f"clname={clname} pages={len(pages)}")
                break
            time.sleep(5)
            waits += 1

        assert status == cb.CrawlStatus.SUCCEEDED

        logging.info(f"clname={clname} root_url={root_url}, "
                     f"crawl_id={crawl_id} status={status} pages={len(pages)}")

        col.delete_crawl(root_url)

        col.index_crawl(crawl_id)

    def ask(self, clname: str, q: str, top_k: int = 5):
        col = cb.Collection(name=clname)
        resp = col.ask(q, top_k)
        logging.info(f"{clname} q={q} a={resp.answer}")
        doc_names = [ref.doc_name for ref in resp.refs]
        logging.info(f"refs={doc_names}")

    def manual_test_doc_apis(self):
        cb.init(api_key=self.apikey, account_id=self.aid)
        clname = 'test_doc_apis'
        col = cb.Collection(name=clname)
        cb.create_collection(col)

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

            resp = chat2.ask("q1")
            self.assertRefsAreFromDoc(resp.refs, "text_file.txt")
            resp = chat2.ask("q2")
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

    def test_regress_acc(self):
        cb.init(api_key=self.apikey, account_id=self.aid)

        cols = cb.list_collections()
        logging.info(f"cols={cols}")

        clname1 = 'llm_research_test'
        clname2 = 'regress_pngame_docs'
        self._test_doc_and_web(clname1, clname2, write=False)

        clname1 = 'llm_research_test_write'
        clname2 = 'regress_pngame_docs_write'
        #cb.delete_collection(clname2)
        #col = cb.Collection(name=clname2)
        #cb.create_collection(col)
        self._test_doc_and_web(clname1, clname2, write=True)

        self._test_transcribe_audio(clname1)

        self._test_confluence_user()
        self._test_connector_ingests()

    def _test_doc_and_web(self, clname1: str, clname2: str, write: bool = True):
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
        if write:
            self.crawl_web(clname2, 'https://docs.piratenation.game/archive')

        docs = col.list_documents()
        docs.sort()
        logging.info(f"docs={len(docs)} {docs}")

        q = 'what is pirate nation?'
        self.ask(clname2, q)

    def _test_transcribe_audio(self, clname1: str):
        col = cb.Collection(name=clname1)

        # transcribe a audio file
        audio_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/test_audio.mp3'
        trans = "0.0 - 4.0: それでは、仕入れ割引について見ていきたいと思います。\n"
        resp = col.transcribe_audio(audio_file, 'ja')
        assert resp.transcript == trans

        # transcribe a audio file hosted on a site
        audio_file_url = 'https://www.chatbees.ai/images/audio/test_5s.mp3'
        resp = col.transcribe_audio(audio_file_url, 'ja')
        assert resp.transcript == trans

    def _test_confluence_user(self):
        clname = 'confluence_test'
        # TODO fix stale cache
        #cb.delete_collection(clname)
        #col = cb.Collection(name=clname)
        #cb.create_collection(col)

        self._test_confluence(clname, TEST_CONFLUENCE_USER, TEST_CONFLUENCE_TOKEN)
        self._test_confluence_cql(clname, TEST_CONFLUENCE_USER, TEST_CONFLUENCE_TOKEN)

    def _test_confluence(self, clname: str, user: str = None, token: str = None):
        schedule = cb.ScheduleSpec(cron_expr='0 0 * * 0', timezone='UTC')
        spec = cb.ConfluenceSpec(schedule=schedule,
                                  url=TEST_CONFLUENCE_URL,
                                  username=user,
                                  token=token,
                                  space=TEST_CONFLUENCE_SPACE)

        self._test_ingestion(clname, cb.IngestionType.CONFLUENCE, spec)

        # delete the periodic ingestion
        col = cb.Collection(name=clname)
        col.delete_periodic_ingestion(cb.IngestionType.CONFLUENCE)
        cb.describe_collection(clname)

    def _test_confluence_cql(self, clname: str, user: str = None, token: str = None):
        cql = f"type = page and space = '{TEST_CONFLUENCE_SPACE}' and lastModified >= '2024-02-17'"

        cron_expr = '0 0 * * *'
        schedule = cb.ScheduleSpec(cron_expr=cron_expr, timezone='UTC')
        spec = cb.ConfluenceSpec(schedule=schedule,
                                  url=TEST_CONFLUENCE_URL,
                                  username=user,
                                  token=token,
                                  cql=cql)

        self._test_ingestion(clname, cb.IngestionType.CONFLUENCE, spec)

        # update the periodic ingestion
        if os.environ.get('ENV_TEST_CRON', default='False').lower() == "true":
            cron_expr = '*/2 * * * *'
        schedule = cb.ScheduleSpec(cron_expr=cron_expr, timezone='UTC')
        spec = cb.ConfluenceSpec(schedule=schedule,
                                  url=TEST_CONFLUENCE_URL,
                                  username=user,
                                  token=token,
                                  cql=cql)
        col = cb.Collection(name=clname)
        col.update_periodic_ingestion(cb.IngestionType.CONFLUENCE, spec)
        cb.describe_collection(clname)

        if os.environ.get('ENV_TEST_CRON', default='False').lower() == "true":
            logging.info(f"sleep 180s for periodic crawl to run")
            time.sleep(180)
        col.delete_periodic_ingestion(cb.IngestionType.CONFLUENCE)

    def _test_connector_ingests(self):
        clname = 'ingest_test'
        #cb.delete_collection(clname)
        #col = cb.Collection(name=clname)
        #cb.create_collection(col)

        self._test_confluence(clname)
        self._test_confluence_cql(clname)
        self._test_gdrive(clname)
        self._test_notion(clname)

    def _test_gdrive(self, clname: str):
        spec = cb.GDriveSpec()
        self._test_ingestion(clname, cb.IngestionType.GDRIVE, spec)

    def _test_notion(self, clname: str):
        spec = cb.NotionSpec()
        self._test_ingestion(clname, cb.IngestionType.NOTION, spec)

    def _test_ingestion(self, clname: str, ingestion_type: cb.IngestionType, spec: Any):
        connectors = cb.list_connectors()
        connector_id = ""
        for connector in connectors:
            if connector.type == ingestion_type:
                connector_id = connector.id
                break
        if connector_id == "":
            raise ValueError(f"internal error - data source not connected, "
                             f"{ingestion_type}")

        col = cb.Collection(name=clname)
        ingest_id = col.create_ingestion(connector_id, ingestion_type, spec)
        max_waits = 10
        waits = 0
        while waits < max_waits:
            status = col.get_ingestion(ingest_id)
            if status != cb.IngestionStatus.RUNNING:
                break
            time.sleep(3)
            waits += 1

        # index the crawled pages into the collection
        col.index_ingestion(ingest_id)

        logging.info(f"Ingest pages from {ingestion_type}:")
        for doc in col.list_documents():
            logging.info(f"\t{doc}")

        # ask a question
        q = "what is chatbees?"
        resp = col.ask(q)
        logging.info(f"Question: {q}")
        logging.info(f"Answer: {resp.answer}\n")
