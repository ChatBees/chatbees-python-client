# chatbees-python-client
Python client for [ChatBees](http://www.chatbees.ai), a Serverless Platform for your LLM Apps. ChatBees provides simple and scalable APIs, enabling you to craft a LLM app for your knowledge base in mere minutes.

We're actively improving the product and releasing new features, and we'd love to hear your feedback!
Please take a moment to fill out this [feedback form](https://forms.gle/pif6Vx2LqPjW5v4w5) to help us understand your use-case better.

Signup with your Google or Microsoft account on https://www.chatbees.ai.

ChatBees python client provides very simple APIs for you to directly upload files, crawl websites, ingest data sources including Confluence, Notion and Google Drive. Then you can simply ask questions.


## Quickstart

You can try out ChatBees in just a few lines of code. You can create your own collections, upload files, then get answers  specific to your data assets. The following example walks you through the process of creating a collection and indexing [the original transformer paper](https://arxiv.org/abs/1706.03762) into that collection.

```python
import chatbees as cb

# Create an API key on UI after signup/signin.
# Configure cb to use the newly minted API key.
cb.init(api_key=my_api_key, account_id=your_account_id)

# Create a new collection
llm_research = cb.Collection(name="llm_research")
cb.create_collection(llm_research)

# Index the original Transformer paper into this collection.
llm_research.upload_document("https://arxiv.org/pdf/1706.03762.pdf")

# Get answers from this paper
llm_research.ask("what is a transformer?")

```

## Installation

Install a released ChatBees python client from pip.

python3 version ```>= 3.10``` is required

```shell
pip3 install chatbees-python-client
```



In the following examples, we will assume you have signup with your google account.

## Creating a Collection
You can create a collection that is only accessible with a specific API key.

```python
import chatbees as cb

cb.init(api_key=my_api_key, account_id=your_account_id)

# Create a collection called llm_research
collection = cb.Collection(name='llm_research')
cb.create_collection(collection)
```

## Listing collection
You can see list of collections you have access to. For example, this list 
will include all collections that were created using the currently configured 
API key.

```python
import chatbees as cb

cb.init(api_key=my_api_key, account_id=your_account_id)

collections = cb.list_collections()
```


## Uploading a document
You can upload a local file or a file from a web URL and index it into a 
collection.

**Supported file format**
- ```.pdf``` PDF files
- ```.csv``` CSV files
- ```.txt``` Plain-text files
- ```.md```  Markdown files
- ```.docx``` Microsoft word documents

```python
import chatbees as cb

cb.init(api_key=my_api_key, account_id=your_account_id)

# llm_research collection was created in the previous step
collection = cb.collection('llm_research')

# Local file and URLs are both supported.
# URL must contain the full scheme prefix (http:// or https://)
collection.upload_document('/path/to/file.pdf')
collection.upload_document('https://path/to/file.pdf')
```

## Crawl a website
You can pass the website root url. ChatBees will automatically crawl it.

```python
import chatbees as cb

cb.init(api_key=my_api_key, account_id=your_account_id)

# Create the crawl task
collection = cb.Collection(name='example-web')
cb.create_collection(collection)

root_url = 'https://www.example.com'
crawl_id = collection.create_crawl(root_url)

# Query the crawl status
resp = collection.get_crawl(crawl_id)

# If re-crawl the same root_url, delete the old indexed crawl results
collection.delete_crawl(root_url)

# check resp.crawl_status becomes CrawlStatus.SUCCEEDED, and index the pages
collection.index_crawl(crawl_id)
```

## Asking a question
You can ask questions within a collection. API key is required for private
collections only. ```ask()``` method returns a plain-text answer to 
your question, as well as a list of most relevance references used to derive 
the answer. 

```python
import chatbees as cb

cb.init(api_key=my_api_key, account_id=your_account_id)

# Get a plain text answer, as well as a list of references from the collection
# that are the most relevant to the question.
answer, refs = cb.collection('llm_research').ask('what is a transformer?')
```

## Deleting a collection
You can delete a collection using the same API key that was used to create it.

```python
import chatbees as cb

cb.init(api_key=my_api_key, account_id=your_account_id)

cb.delete_collection('llm_research')
```
