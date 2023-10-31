# nautilusdb-python-client
Python client for [NautilusDB](http://nautilusdb.com), a fully-managed, 
cloud-native vector search service.

NautilusDB is currently in <ins>**public alpha**</ins>. We're actively 
improving 
the 
product and releasing new features and we'd love to hear your feedback! 
Please take a moment to fill out this [feedback form](https://docs.google.com/forms/d/e/1FAIpQLSdAB6FLU91oUBJVRcPtpEK3WpgL9cVWethFHx0gAkKhg7LjrQ/viewform) to help us understand your use-case better.

## Quick start

You can try out NautilusDB in just a few lines of code. We have 
prepared a special public collection ```openai-web``` that can answer 
questions about the contents of ```www.openai.com``` 
```python
import nautilusdb as ndb

answer, _ = ndb.collection('openai-web').ask('what is red team?')
print(answer)
"""
Sample answer:

Red team refers to the group of external experts who work with OpenAI to
identify and evaluate potential risks and harmful capabilities in new systems.
The red team's role is to help develop taxonomies of risk and provide input
throughout the model and product development lifecycle.
"""

```
You can also create your own collections, upload files, then get answers 
specific to your data assets. The following example walks you through the 
process of creating a collection and indexing [the original transformer paper](https://arxiv.org/abs/1706.03762) into that collection.

```python
import nautilusdb as ndb

# Create an API key
my_api_key = ndb.create_api_key()

# Configure ndb to use the newly minted API key
ndb.init(api_key=my_api_key)

# Create a new collection with preconfigured dimension
llm_research = ndb.CollectionBuilder.question_answer(name="llm_research").build()
ndb.create_collection(llm_research)

# Index the original Transformer paper into this collection.
llm_research.upload_document("https://arxiv.org/pdf/1706.03762.pdf")

# Get answers from this paper
llm_research.ask("what is a transformer?")

```

## Installation

Install a released NautilusDB python client from pip.

python3 version ```>= 3.10``` is required

```shell
pip3 install nautilusdb
```

## Creating an API key
You can create an API key and use it to create or access your own collections.  
In public preview, all collections are created inside a shared, public 
account. Private accounts and related functionalities will be released soon.

```python
import nautilusdb as ndb

# Create a new API key
my_api_key = ndb.create_api_key()

# Please record this API key and keep it a secrete
#
# Collections created with this key can only be accessed
# through this key!
print(my_api_key)

# Use this API key in all subsequent calls
ndb.init(api_key=my_api_key)
```

## Creating a Collection
See [this page](https://www.nautilusdb.com/developers.html) for a brief overview of NautilusDB data model 

You can create a public collection that is accessible to everyone, or a 
private collection only accessible with a specific API key.

```python
import nautilusdb as ndb

# Set an API key to create a private collection
# Set API key to None to create a public collection
ndb.init(api_key="<my_api_key>")

# Create a collection called c1. c1 is configured to be compatible with 
# Q/A APIs. It has vector embeddings dimension of 1536, contains three metadata
# columns: text (string), tokens (int), filename (string). 
collection = ndb.CollectionBuilder.question_answer('llm_research').build()
ndb.create_collection(collection)
```

## Uploading a document
You can upload a local file or a file from a web URL and index it into a 
collection.

**Supported file format**
- ```.pdf``` PDF files
- ```.txt``` Plain-text files
- ```.md```  Markdown files
- ```.docx``` Microsoft word documents

```python
import nautilusdb as ndb

# Optional API key to access private collections
ndb.init(api_key="<my_api_key>")

# Local file and URLs are both supported.
# URL must contain the full scheme prefix (http:// or https://)
ndb.collection('llm_research').upload_document('/path/to/file.pdf')
ndb.collection('llm_research').upload_document('https://path/to/file.pdf')

```

## Asking a question
You can ask questions within a collection. API key is required for private
collections only.

**Available public collections**
- ```openai-web```: Contains contents of ```www.openai.com```

```python
import nautilusdb as ndb

# Optional API key to access private collections
ndb.init(api_key="<my_api_key>")

# Get a plain text answer, as well as a list of references from the collection
# that are the most relevant to the question.
answer, refs = ndb.collection('openai-web').ask('what is red team?')


answer, refs = ndb.collection('llm_research').ask('what is a transformer?')
```
