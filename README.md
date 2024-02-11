# chatbees-python-client
Python client for [ChatBees](http://www.chatbees.ai), a Serverless Platform for your LLM Apps. ChatBees provides simple and scalable APIs, enabling you to craft a LLM app for your knowledge base in mere minutes.

ChatBees is currently in <ins>**public alpha**</ins>. We're actively improving 
the product and releasing new features, and we'd love to hear your feedback! 
Please take a moment to fill out this [feedback form](https://forms.gle/pif6Vx2LqPjW5v4w5) to help us understand your use-case better.

Signup with your google account on https://www.chatbees.ai. You could also try it out in ChatBees public account without signup.

> For the public account, by default, all collections are subject to permanent deletion after 2 weeks. Please let us know if you need to keep it for longer via the feedback form.

ChatBees python client provides very simple APIs for you to directly upload files and ask questions.


## Quickstart

You can try out ChatBees in just a few lines of code. You can create your own collections, upload files, then get answers  specific to your data assets. The following example walks you through the process of creating a collection and indexing [the original transformer paper](https://arxiv.org/abs/1706.03762) into that collection.

```python
import chatbees as cdb

# If you signup with your google account, you will create an API key on UI and skip this step.
# Create an API key in the public account.
# my_api_key = cdb.create_api_key()

# Configure cdb to use the newly minted API key.
cdb.init(api_key=my_api_key, account_id=your_account_id)
# If you use the public account, not need to configure the account_id.
# cdb.init(api_key=my_api_key)

# Create a new collection
llm_research = cdb.Collection(name="llm_research")
cdb.create_collection(llm_research)

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

## Creating an API key
You need an API key to create, update, delete own collections. A collection 
can only be accessed by the API key that created it.

Account management and related functionalities will be released soon.

```python
import chatbees as cdb

# If you signup with your google account, you will create an API key on UI and skip this step.
# Create an API key in the public account.
# my_api_key = cdb.create_api_key()

# Please record this API key and keep it a secrete
#
# Collections created with this key can only be accessed
# through this key!
print(my_api_key)

# Use this API key in all subsequent calls
cdb.init(api_key=my_api_key, account_id=your_account_id)
# If you use the public account, not need to configure the account_id.
# cdb.init(api_key=my_api_key)


```

In the following examples, we will assume you have signup with your google account.

## Creating a Collection
You can create a collection that is only accessible with a specific API key.

```python
import chatbees as cdb

cdb.init(api_key=my_api_key, account_id=your_account_id)

# Create a collection called llm_research
collection = cdb.Collection(name='llm_research')
cdb.create_collection(collection)
```

## Listing collection
You can see list of collections you have access to. For example, this list 
will include all collections that were created using the currently configured 
API key.

```python
import chatbees as cdb

cdb.init(api_key=my_api_key, account_id=your_account_id)

collections = cdb.list_collections()
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
import chatbees as cdb

cdb.init(api_key=my_api_key, account_id=your_account_id)

# llm_research collection was created in the previous step
collection = cdb.collection('llm_research')

# Local file and URLs are both supported.
# URL must contain the full scheme prefix (http:// or https://)
collection.upload_document('/path/to/file.pdf')
collection.upload_document('https://path/to/file.pdf')
```

## Crawl a website
You can pass the website root url. ChatBees will automatically crawl it.

```python
import chatbees as cdb

cdb.init(api_key=my_api_key, account_id=your_account_id)

# Create the crawl task
collection = cdb.Collection(name='example-web')
cdb.create_collection(collection)

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

**Available public collections that do not require an API key to access**
- ```openai-web```: Contains contents of ```www.openai.com```

```python
import chatbees as cdb

cdb.init(api_key=my_api_key, account_id=your_account_id)

# Get a plain text answer, as well as a list of references from the collection
# that are the most relevant to the question.
answer, refs = cdb.collection('openai-web').ask('what is red team?')

answer, refs = cdb.collection('llm_research').ask('what is a transformer?')
```

## Deleting a collection
You can delete a collection using the same API key that was used to create it.

```python
import chatbees as cdb

cdb.init(api_key=my_api_key, account_id=your_account_id)

cdb.delete_collection('llm_research')
```
