# nautilusdb-python-client
Python client for [NautilusDB](http://nautilusdb.com), a fully-managed, 
cloud-native vector search service.

NautilusDB is currently in <ins>**public alpha**</ins>. We're actively improving 
the product and releasing new features, and we'd love to hear your feedback! 
Please take a moment to fill out this [feedback form](https://forms.gle/pif6Vx2LqPjW5v4w5) to help us understand your use-case better.

> By default, all collections are subject to permanent deletion after 2 weeks. Please let us know if you need to keep it for longer via the feedback form.

NautilusDB python client supports both high-level APIs where you can 
directly upload files and ask questions, as well as a set of low-level APIs 
to use it as a vector database to directly manipulate vectors.

**Continue reading, or [Click here](#creating-a-collection) to see high-level API guide.** \
**[Click here](#using-nautilusdb-as-a-vector-database) to see vector database API guide**

## Quickstart

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
pip3 install nautilusdb-client
```

## Creating an API key
You need an API key to create, update, delete own collections. A collection 
can only be accessed by the API key that created it.

Account management and related functionalities will be released soon.

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

You can create a collection that is only accessible with a specific API key.

```python
import nautilusdb as ndb

ndb.init(api_key="<my_api_key>")

# Create a collection called c1. c1 is configured to be compatible with 
# Q/A APIs. It has vector embeddings dimension of 1536, contains three metadata
# columns: text (string), tokens (int), filename (string). 
collection = ndb.CollectionBuilder.question_answer('llm_research').build()
ndb.create_collection(collection)
```

## Listing collection
You can see list of collections you have access to. For example, this list 
will include all collections that were created using the currently configured 
API key.

```python
import nautilusdb as ndb

ndb.init(api_key="<my_api_key>")

collections = ndb.list_collections()
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

ndb.init(api_key="<my_api_key>")

# llm_research collection was created in the previous step
collection = ndb.collection('llm_research')

# Local file and URLs are both supported.
# URL must contain the full scheme prefix (http:// or https://)
collection.upload_document('/path/to/file.pdf')
collection.upload_document('https://path/to/file.pdf')
```

## Asking a question
You can ask questions within a collection. API key is required for private
collections only. ```ask()``` method returns a plain-text answer to 
your question, as well as a list of most relevance references used to derive 
the answer. 

**Available public collections that do not require an API key to access**
- ```openai-web```: Contains contents of ```www.openai.com```

```python
import nautilusdb as ndb

# Get a plain text answer, as well as a list of references from the collection
# that are the most relevant to the question.
answer, refs = ndb.collection('openai-web').ask('what is red team?')

ndb.init(api_key="<my_api_key>")
answer, refs = ndb.collection('llm_research').ask('what is a transformer?')
```

## Deleting a collection
You can delete a collection using the same API key that was used to create it.

```python
import nautilusdb as ndb

ndb.init(api_key="<my_api_key>")

ndb.delete_collection('llm_research')
```


## Using NautilusDB as a vector database
NautilusDB is a vector database at its core. You can directly manipulate 
vectors in the database.

### Creating a custom collection 
Create a collection where vectors have embedding dimension of ```2``` and two 
metadata columns, ```int_col``` of type ```Int``` and ```str_col``` of type ```String```.
Currently, we use ```L2``` as the vector distance metric. Support for other 
distance metrics will be available soon.

```python
import nautilusdb as ndb

ndb.init(api_key='<my_api_key>')

# Create a collection with two metadata columns
col = (ndb.CollectionBuilder() 
      .set_name('custom_collection')
      .set_dimension(2)
      .add_metadata_column('int_col', ndb. ColumnType.Int)
      .add_metadata_column('str_col', ndb.ColumnType.String).build())

ndb.create_collection(col)
```

### Upserting vectors into the collection
You can now upsert vectors into the collection. Metadata columns have 
default value of ```null```. You can overwrite this default by setting
```metadata``` field of the vector.

```python
import nautilusdb as ndb

ndb.init(api_key='<my_api_key>')

# Upsert 6 vectors. Some with one metadata column, others with two
col = ndb.collection('custom_collection')
col.upsert_vector([
    ndb.Vector(vid='1', embedding=[0.1, 0.1], metadata={'int_col': 1, 'str_col': 'vector at 0.1, 0.1'}),
    ndb.Vector(vid='2', embedding=[0.2, 0.2], metadata={'int_col': 2, 'str_col': 'vector at 0.2, 0.2'}),
    ndb.Vector(vid='3', embedding=[0.3, 0.3], metadata={'int_col': 3, 'str_col': 'vector at 0.3, 0.3'}),
    ndb.Vector(vid='100', embedding=[0.4, 0.4], metadata={'int_col': 100}),
    ndb.Vector(vid='200', embedding=[0.5, 0.5], metadata={'int_col': 200}),
    ndb.Vector(vid='300', embedding=[0.6, 0.6], metadata={'int_col': 300}),
])
```

### Describing a collection with stats
You can retrieve collection configurations as well as simple statistics 
about the collection via ```describe``` API.

```python
import nautilusdb as ndb

ndb.init(api_key='<my_api_key>')

# Retrieve collection config and stats
col = ndb.describe_collection('custom_collection')
print(f"Collection {col.name} has {col.stats.vector_count} vectors!")
```

### Deleting vectors from a collection
You can delete vectors from the collection. We support three deletion conditions
- <ins>**Delete by ID**</ins>
  - You can delete a set of vectors by their IDs
- <ins>**Delete by metadata filter**</ins>
  - You can delete all vectors that satisfy a metadata filter
- <ins>**Delete all**</ins>
  - You can delete all vectors from a collection

Exactly one condition can be specified in each API call.

```python
import nautilusdb as ndb

ndb.init(api_key='<my_api_key>')

col = ndb.collection('custom_collection')

# Delete 3 vectors, 'foo', 'bar', and 'baz'.
col.delete_vectors(vector_ids=['foo', 'bar', 'baz'])

# Delete all vectors where 'int_col' is specified, and the value is less than 3.
col.delete_vectors(metadata_filter="int_col < 3")

# Delete all vectors in the collection
col.delete_vectors(delete_all=True)

```

### Searching a collection
You can search a collection with a set of vectors, as well as a set of optional 
metadata column filters. Metadata filter is SQL-compatible and supports a wide 
range of operators, including:
- Comparison Operators: ```=```, ```<```, ```>```, ```<=```, ```>=```, ```!=```
- Boolean Operators: ```and```, ```or```, ```not```
- Grouping Operators: ```()```
- Null Check:  ```is null```, ```is not null```

```python
import nautilusdb as ndb

ndb.init(api_key='<my_api_key>')

col = ndb.collection('custom_collection')

# Search
col.search(
    [
        # Closest vectors are 1, 2, 3
        ndb.SearchRequest(embedding=[0.1, 0.1]),

        # Closest vectors are 2, 3, 100 (1 is filered out)
        ndb.SearchRequest(embedding=[0.1, 0.1], metadata_filter='int_col != 1'),

        # Closest vectors is 1 (2, 3, etc are filtered out)
        ndb.SearchRequest(embedding=[0.1, 0.1], metadata_filter='int_col = 1'),

        # Closest vectors are 100, 200, 300
        ndb.SearchRequest(
            embedding=[0.1, 0.1], metadata_filter='str_col is null'),
    ])
```
### Querying a collection
You can also perform a pure metadata query against vectors in a collection 
using metadata filter (see search documentation above for filter syntax).

Currently, returned vectors are not ranked. We're working on supporting text 
search with relevance scoring soon, stay tuned!


```python
import nautilusdb as ndb

ndb.init(api_key='<my_api_key>')

col = ndb.collection('custom_collection')

# Metadata query
col.query(
    [
        ndb.QueryRequest(metadata_filter='int_col != 1'),
        ndb.QueryRequest(metadata_filter='int_col = 1'),
        ndb.QueryRequest(metadata_filter='str_col is null'),
    ])
```
